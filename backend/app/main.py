from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field
from uuid import UUID
import httpx, json
from .config import settings

app = FastAPI(title="Zero-Token Voice Receptionist", version="0.1.0")

class TurnRequest(BaseModel):
    tenant_id: UUID
    session_id: UUID
    text: str = Field(min_length=1, max_length=8000)
    language: str = "auto"

class TurnResponse(BaseModel):
    reply: str
    session_id: UUID

SYSTEM_PROMPT = """You are a helpful, concise business receptionist.
Answer only using supplied business context when factual. If unsure, say you will
take a message and have a staff member follow up. Never invent prices, availability,
policies, or appointments. Respond in the caller's language when possible."""

@app.get("/health")
async def health():
    return {"status": "ok", "service": "voice-receptionist"}

async def generate_reply(tenant_id: UUID, session_id: UUID, text: str) -> str:
    # TODO: Load tenant-scoped RAG chunks and rolling transcript from Postgres/Redis.
    messages = [{"role":"system","content":SYSTEM_PROMPT},
                {"role":"user","content":text}]
    try:
        async with httpx.AsyncClient(timeout=90) as client:
            r = await client.post(f"{settings.ollama_url}/api/chat",
                json={"model":settings.ollama_model,"messages":messages,"stream":False})
            r.raise_for_status()
            return r.json()["message"]["content"].strip()
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=503, detail=f"Local model unavailable: {exc}")

@app.post("/v1/turn", response_model=TurnResponse)
async def turn(body: TurnRequest):
    reply = await generate_reply(body.tenant_id, body.session_id, body.text)
    return TurnResponse(reply=reply, session_id=body.session_id)

@app.websocket("/v1/stream/{tenant_id}/{session_id}")
async def stream(ws: WebSocket, tenant_id: UUID, session_id: UUID):
    # Text-turn websocket scaffold; audio/WebRTC transport is not wired yet.
    await ws.accept()
    try:
        while True:
            incoming = await ws.receive_text()
            data = json.loads(incoming)
            text = str(data.get("text","")).strip()
            if not text: continue
            reply = await generate_reply(tenant_id, session_id, text)
            await ws.send_json({"type":"reply","text":reply,"session_id":str(session_id)})
    except WebSocketDisconnect:
        return
