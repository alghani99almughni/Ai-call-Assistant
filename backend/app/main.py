from fastapi import FastAPI,WebSocket,WebSocketDisconnect,Depends
from pydantic import BaseModel,Field
from uuid import UUID
import json
from .routes import router,grounded_reply
from .telephony import router as telephony_router
from .phone_setup import router as phone_router
from .schemas import MessageIn
from .security import current_user,tenant_access
from .models import User
from .db import engine,Base
app=FastAPI(title="Zero-Token Voice Receptionist",version="0.5.0")
app.include_router(router);app.include_router(telephony_router);app.include_router(phone_router)
@app.on_event("startup")
async def startup():
 async with engine.begin() as conn:await conn.run_sync(Base.metadata.create_all)
class TurnRequest(BaseModel):tenant_id:UUID;session_id:UUID;text:str=Field(min_length=1,max_length=8000)
class TurnResponse(BaseModel):reply:str;session_id:UUID
@app.get("/health")
async def health():return {"status":"ok","service":"voice-receptionist"}
@app.post("/v1/turn",response_model=TurnResponse)
async def turn(body:TurnRequest,user:User=Depends(current_user)):
 tenant_access(body.tenant_id,user);result=await grounded_reply(body.tenant_id,body.session_id,MessageIn(content=body.text),user);return TurnResponse(reply=result["reply"],session_id=body.session_id)
@app.websocket("/v1/stream/{tenant_id}/{session_id}")
async def stream(ws:WebSocket,tenant_id:UUID,session_id:UUID):
 token=ws.query_params.get("token")
 if not token:await ws.close(code=1008);return
 from jose import jwt,JWTError
 from .config import settings
 from .db import SessionLocal
 try:
  claims=jwt.decode(token,settings.app_secret,algorithms=["HS256"])
  if claims.get("tenant")!=str(tenant_id):await ws.close(code=1008);return
  async with SessionLocal() as db:user=await db.get(User,claims.get("sub"))
  if not user or not user.is_active or user.tenant_id!=tenant_id:await ws.close(code=1008);return
 except (JWTError,ValueError):await ws.close(code=1008);return
 await ws.accept()
 try:
  while True:
   payload=json.loads(await ws.receive_text());text=str(payload.get("text","")).strip()
   if text:
    result=await grounded_reply(tenant_id,session_id,MessageIn(content=text),user);await ws.send_json({"type":"reply","text":result["reply"],"sources":result["sources"]})
 except WebSocketDisconnect:return
