from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field
from uuid import UUID
import httpx, json
from .config import settings
from .routes import router
from .db import engine, Base

app = FastAPI(title="Zero-Token Voice Receptionist", version="0.2.0")
app.include_router(router)

@app.on_event("startup")
async def startup():
    # Development convenience only. Use Alembic migrations in production.
    async with engine.begin() as conn: await conn.run_sync(Base.metadata.create_all)

class TurnRequest(BaseModel):
    tenant_id: UUID
    session_id: UUID
    text: str = Field(min_length=1, max_length=8000)
    language: str = "auto"
class TurnResponse(BaseModel):
    reply: str
    session_id: UUID

@app.get("/health")
async def health(): return {"status":"ok","service":"voice-receptionist"}

@app.post("/v1/turn",response_model=TurnResponse)
async def turn(body:TurnRequest):
    from .routes import grounded_reply
    from .schemas import MessageIn
    result=await grounded_reply(body.tenant_id,body.session_id,MessageIn(content=body.text))
    return TurnResponse(reply=result["reply"],session_id=body.session_id)

@app.websocket("/v1/stream/{tenant_id}/{session_id}")
async def stream(ws:WebSocket,tenant_id:UUID,session_id:UUID):
    # Text-only socket scaffold; WebRTC/SIP media not connected in this version.
    await ws.accept()
    try:
        while True:
            payload=json.loads(await ws.receive_text())
            text=str(payload.get("text","")).strip()
            if not text: continue
            from .routes import grounded_reply
            from .schemas import MessageIn
            result=await grounded_reply(tenant_id,session_id,MessageIn(content=text))
            await ws.send_json({"type":"reply","text":result["reply"],"sources":result["sources"]})
    except WebSocketDisconnect: return
