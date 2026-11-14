"""Authenticated tenant-scoped API."""
from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy import select, desc
from uuid import UUID
from .db import SessionLocal
from .models import Tenant,CallSession,CallMessage,KnowledgeChunk,User
from .schemas import TenantCreate,TenantOut,CallOut,MessageIn,KnowledgeIn,SignupIn,LoginIn,TokenOut
from .rag import embed,embed_query,ollama_chat,build_context
from .security import current_user,tenant_access,hash_password,verify_password,create_token
router=APIRouter(prefix="/v1")
@router.post("/auth/signup",response_model=TokenOut)
async def signup(body:SignupIn):
    async with SessionLocal() as db:
        if await db.scalar(select(User).where(User.email==body.email.lower())): raise HTTPException(409,"Email already registered")
        if await db.scalar(select(Tenant).where(Tenant.slug==body.slug)): raise HTTPException(409,"Business slug already taken")
        tenant=Tenant(name=body.business_name,slug=body.slug,industry=body.industry.lower()); db.add(tenant); await db.flush()
        user=User(tenant_id=tenant.id,email=body.email.lower(),password_hash=hash_password(body.password),role="admin")
        db.add(user); await db.commit(); await db.refresh(user)
        return TokenOut(access_token=create_token(user),user=user)
@router.post("/auth/login",response_model=TokenOut)
async def login(body:LoginIn):
    async with SessionLocal() as db:
        user=await db.scalar(select(User).where(User.email==body.email.lower()))
        if not user or not verify_password(body.password,user.password_hash): raise HTTPException(401,"Incorrect email or password",headers={"WWW-Authenticate":"Bearer"})
        if not user.is_active: raise HTTPException(403,"Account disabled")
        return TokenOut(access_token=create_token(user),user=user)
@router.get("/auth/me")
async def me(user:User=Depends(current_user)): return {"id":user.id,"email":user.email,"role":user.role,"tenant_id":user.tenant_id}
@router.post("/tenants",response_model=TenantOut)
async def create_tenant(body:TenantCreate,user:User=Depends(current_user)):
    if user.role!="platform_admin": raise HTTPException(403,"Platform admin required")
    async with SessionLocal() as db:
        row=Tenant(**body.model_dump()); db.add(row)
        try: await db.commit()
        except Exception: await db.rollback(); raise HTTPException(409,"Tenant slug already exists")
        await db.refresh(row); return row
@router.get("/tenants/{tenant_id}",response_model=TenantOut)
async def get_tenant(tenant_id:UUID,user:User=Depends(current_user)):
    tenant_access(tenant_id,user)
    async with SessionLocal() as db:
        row=await db.get(Tenant,tenant_id)
        if not row: raise HTTPException(404,"Tenant not found")
        return row
@router.post("/tenants/{tenant_id}/calls",response_model=CallOut)
async def create_call(tenant_id:UUID,caller_number:str|None=None,user:User=Depends(current_user)):
    tenant_access(tenant_id,user)
    async with SessionLocal() as db:
        if not await db.get(Tenant,tenant_id): raise HTTPException(404,"Tenant not found")
        row=CallSession(tenant_id=tenant_id,caller_number=caller_number); db.add(row); await db.commit(); await db.refresh(row); return row
@router.get("/tenants/{tenant_id}/calls",response_model=list[CallOut])
async def list_calls(tenant_id:UUID,limit:int=Query(50,ge=1,le=200),user:User=Depends(current_user)):
    tenant_access(tenant_id,user)
    async with SessionLocal() as db: return (await db.scalars(select(CallSession).where(CallSession.tenant_id==tenant_id).order_by(desc(CallSession.started_at)).limit(limit))).all()
@router.post("/tenants/{tenant_id}/calls/{call_id}/messages")
async def add_message(tenant_id:UUID,call_id:UUID,body:MessageIn,user:User=Depends(current_user)):
    tenant_access(tenant_id,user)
    if body.role not in ("user","assistant"): raise HTTPException(400,"role must be user or assistant")
    async with SessionLocal() as db:
        call=await db.scalar(select(CallSession).where(CallSession.id==call_id,CallSession.tenant_id==tenant_id))
        if not call: raise HTTPException(404,"Call not found")
        db.add(CallMessage(tenant_id=tenant_id,session_id=call_id,role=body.role,content=body.content)); await db.commit(); return {"saved":True}
@router.post("/tenants/{tenant_id}/knowledge")
async def add_knowledge(tenant_id:UUID,body:KnowledgeIn,user:User=Depends(current_user)):
    tenant_access(tenant_id,user); pieces=[body.content[i:i+900] for i in range(0,len(body.content),750)]
    async with SessionLocal() as db:
        if not await db.get(Tenant,tenant_id): raise HTTPException(404,"Tenant not found")
        for piece in pieces: db.add(KnowledgeChunk(tenant_id=tenant_id,source_name=body.source_name,content=piece,embedding=embed(piece)))
        await db.commit()
    return {"chunks_added":len(pieces)}
@router.post("/tenants/{tenant_id}/calls/{call_id}/reply")
async def grounded_reply(tenant_id:UUID,call_id:UUID,body:MessageIn,user:User=Depends(current_user)):
    tenant_access(tenant_id,user)
    async with SessionLocal() as db:
        call=await db.scalar(select(CallSession).where(CallSession.id==call_id,CallSession.tenant_id==tenant_id))
        if not call: raise HTTPException(404,"Call not found")
        vector=embed_query(body.content)
        rows=(await db.scalars(select(KnowledgeChunk).where(KnowledgeChunk.tenant_id==tenant_id,KnowledgeChunk.embedding.is_not(None)).order_by(KnowledgeChunk.embedding.cosine_distance(vector)).limit(4))).all()
        context=build_context([r.content for r in rows])
        history=(await db.scalars(select(CallMessage).where(CallMessage.tenant_id==tenant_id,CallMessage.session_id==call_id).order_by(CallMessage.created_at.desc()).limit(12))).all()
        msgs=[{"role":"system","content":"Receptionist. Use verified context only; do not invent. If missing, offer staff callback. Business context:\n"+context}]
        msgs += [{"role":m.role,"content":m.content} for m in reversed(history)]; msgs.append({"role":"user","content":body.content})
        answer=await ollama_chat(msgs)
        db.add_all([CallMessage(tenant_id=tenant_id,session_id=call_id,role="user",content=body.content),CallMessage(tenant_id=tenant_id,session_id=call_id,role="assistant",content=answer)])
        await db.commit(); return {"reply":answer,"sources":[r.source_name for r in rows]}
