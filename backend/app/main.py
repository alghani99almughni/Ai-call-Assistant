from fastapi import FastAPI,WebSocket,WebSocketDisconnect,Depends
from pydantic import BaseModel,Field
from uuid import UUID
import json
from .routes import router,grounded_reply
from .schemas import MessageIn
from .security import current_user,tenant_access
from .models import User
from .db import engine,Base
app=FastAPI(title="Zero-Token Voice Receptionist",version="0.3.0"); app.include_router(router)
@app.on_event("startup")
async def startup():
    # Development convenience only. Use Alembic migrations in production.
    async with engine.begin() as conn: await conn.run_sync(Base.metadata.create_all)
class TurnRequest(BaseModel):
    tenant_id:UUID; session_id:UUID; text:str=Field(min_length=1,max_length=8000)
class TurnResponse(BaseModel): reply:str; session_id:UUID
@app.get("/health")
async def health(): return {"status":"ok","service":"voice-receptionist"}
@app.post("/v1/turn",response_model=TurnResponse)
async def turn(body:TurnRequest,user:User=Depends(current_user)):
    tenant_access(body.tenant_id,user); result=await grounded_reply(body.tenant_id,body.session_id,MessageIn(content=body.text),user)
    return TurnResponse(reply=result["reply"],session_id=body.session_id)
@app.websocket("/v1/stream/{tenant_id}/{session_id}")
async def stream(ws:WebSocket,tenant_id:UUID,session_id:UUID):
    token=ws.query_params.get("token")
    if not token: await ws.close(code=1008); return
    from .security import current_user
    from jose import jwt,JWTError
    from .config import settings
    try:
        claims=jwt.decode(token,settings.app_secret,algorithms=["HS256"])
        if claims.get("tenant")!=str(tenant_id): await ws.close(code=1008); return
    except JWTError: await ws.close(code=1008); return
    await ws.accept()
    try:
        while True:
            payload=json.loads(await ws.receive_text()); text=str(payload.get("text","")).strip()
            if not text: continue
            result=await grounded_reply(tenant_id,session_id,MessageIn(content=text))
            await ws.send_json({"type":"reply","text":result["reply"],"sources":result["sources"]})
    except WebSocketDisconnect: return
