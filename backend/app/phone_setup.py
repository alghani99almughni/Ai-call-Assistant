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
 phone_number:str=Field(description="E.164 number, e.g. +919876543210")
 provider:str="twilio";provider_number_sid:str|None=None
class PhoneOut(BaseModel):
 phone_number:str;provider:str;enabled:bool;webhook_url:str
def out(row,tenant_id):return PhoneOut(phone_number=row.phone_number,provider=row.provider,enabled=row.enabled,webhook_url=f"{settings.public_base_url}/voice/twilio/{tenant_id}")
@router.get("",response_model=PhoneOut)
async def get_phone(tenant_id:UUID,user:User=Depends(current_user)):
 tenant_access(tenant_id,user)
 async with SessionLocal() as db:
  row=await db.scalar(select(TenantPhone).where(TenantPhone.tenant_id==tenant_id))
  if not row:raise HTTPException(404,"No phone number configured")
  return out(row,tenant_id)
@router.put("",response_model=PhoneOut)
async def save_phone(tenant_id:UUID,body:PhoneSetupIn,user:User=Depends(current_user)):
 tenant_access(tenant_id,user);number=body.phone_number.strip()
 if not re.fullmatch(r"\+[1-9]\d{7,14}",number):raise HTTPException(422,"Enter E.164 format with country code, e.g. +919876543210")
 if body.provider!="twilio":raise HTTPException(422,"Supported provider: twilio")
 async with SessionLocal() as db:
  if not await db.get(Tenant,tenant_id):raise HTTPException(404,"Tenant not found")
  row=await db.scalar(select(TenantPhone).where(TenantPhone.tenant_id==tenant_id))
  conflict=await db.scalar(select(TenantPhone).where(TenantPhone.phone_number==number))
  if conflict and (not row or conflict.id!=row.id):raise HTTPException(409,"Number assigned to another tenant")
  if row:row.phone_number=number;row.provider=body.provider;row.provider_number_sid=body.provider_number_sid;row.enabled=True
  else:row=TenantPhone(tenant_id=tenant_id,phone_number=number,provider=body.provider,provider_number_sid=body.provider_number_sid);db.add(row)
  await db.commit();return out(row,tenant_id)
@router.delete("")
async def delete_phone(tenant_id:UUID,user:User=Depends(current_user)):
 tenant_access(tenant_id,user)
 async with SessionLocal() as db:
  row=await db.scalar(select(TenantPhone).where(TenantPhone.tenant_id==tenant_id))
  if not row:return {"removed":False}
  await db.delete(row);await db.commit();return {"removed":True}
