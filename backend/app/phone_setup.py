import re
from uuid import UUID
from fastapi import APIRouter,Depends,HTTPException
from pydantic import BaseModel,Field
from sqlalchemy import select
from .db import SessionLocal
from .models import TenantPhone,Tenant,User
from .security import current_user,tenant_access
from .config import settings
router=APIRouter(prefix="/v1/tenants/{tenant_id}/phone",tags=["phone setup"])
class PhoneSetupIn(BaseModel):
 business_name:str=Field(min_length=2,max_length=180)
 phone_number:str=Field(description="Indian mobile in E.164, e.g. +919876543210")
 provider:str="voicelink"
 provider_number_sid:str|None=None
 provider_config:dict={}
class PhoneOut(BaseModel):
 business_name:str;phone_number:str;provider:str;enabled:bool;webhook_url:str
def out(row,tenant_id):return PhoneOut(business_name=row.business_name,phone_number=row.phone_number,provider=row.provider,enabled=row.enabled,webhook_url=f"{settings.public_base_url}/voice/inbound/{tenant_id}")
@router.get("",response_model=PhoneOut)
async def get_phone(tenant_id:UUID,user:User=Depends(current_user)):
 tenant_access(tenant_id,user)
 async with SessionLocal() as db:
  row=await db.scalar(select(TenantPhone).where(TenantPhone.tenant_id==tenant_id))
  if not row:raise HTTPException(404,"No phone configured")
  return out(row,tenant_id)
@router.put("",response_model=PhoneOut)
async def save_phone(tenant_id:UUID,body:PhoneSetupIn,user:User=Depends(current_user)):
 tenant_access(tenant_id,user);number=body.phone_number.strip()
 if not re.fullmatch(r"\+91[6-9]\d{9}",number):raise HTTPException(422,"Enter a valid Indian mobile number in +91XXXXXXXXXX format")
 if body.provider not in ("voicelink","custom_sip"):raise HTTPException(422,"VoiceLink default or custom SIP advanced only")
 async with SessionLocal() as db:
  if not await db.get(Tenant,tenant_id):raise HTTPException(404,"Tenant not found")
  row=await db.scalar(select(TenantPhone).where(TenantPhone.tenant_id==tenant_id))
  conflict=await db.scalar(select(TenantPhone).where(TenantPhone.phone_number==number))
  if conflict and (not row or conflict.id!=row.id):raise HTTPException(409,"Number already assigned to another tenant")
  if row:row.business_name=body.business_name;row.phone_number=number;row.provider=body.provider;row.provider_number_sid=body.provider_number_sid;row.provider_config=body.provider_config;row.enabled=True
  else:row=TenantPhone(tenant_id=tenant_id,business_name=body.business_name,phone_number=number,provider=body.provider,provider_number_sid=body.provider_number_sid,provider_config=body.provider_config);db.add(row)
  await db.commit();return out(row,tenant_id)
@router.delete("")
async def delete_phone(tenant_id:UUID,user:User=Depends(current_user)):
 tenant_access(tenant_id,user)
 async with SessionLocal() as db:
  row=await db.scalar(select(TenantPhone).where(TenantPhone.tenant_id==tenant_id))
  if not row:return {"removed":False}
  await db.delete(row);await db.commit();return {"removed":True}
