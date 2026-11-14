"""Indian telephony inbound event placeholder (VoiceLink/SIP)."""
from fastapi import APIRouter,Request,HTTPException
from sqlalchemy import select
from uuid import UUID
from .db import SessionLocal
from .models import Tenant,TenantPhone,CallSession
router=APIRouter(prefix="/voice",tags=["Indian telephony"])
@router.post("/inbound/{tenant_id}")
async def inbound(tenant_id:UUID,request:Request):
 """Provider event callback only. Media requires SIP/WebSocket voice runtime."""
 form=await request.form();caller=str(form.get("From",form.get("caller","unknown")))[:40]
 async with SessionLocal() as db:
  tenant=await db.get(Tenant,tenant_id);phone=await db.scalar(select(TenantPhone).where(TenantPhone.tenant_id==tenant_id,TenantPhone.enabled.is_(True)))
  if not tenant or not phone:raise HTTPException(404,"Tenant or configured phone not found")
  call=CallSession(tenant_id=tenant_id,caller_number=caller,status="active");db.add(call);await db.commit();await db.refresh(call)
 return {"ok":True,"tenant_id":str(tenant_id),"call_id":str(call.id),"greeting":"Namaste, thank you for calling "+phone.business_name+". How may I help you?","agent_mode":"knowledge_base_default"}
