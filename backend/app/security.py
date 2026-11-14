"""JWT authentication and tenant membership enforcement."""
from datetime import datetime, timedelta, timezone
from hashlib import pbkdf2_hmac
from hmac import compare_digest
import base64, secrets
from jose import jwt, JWTError
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from .config import settings
from .db import SessionLocal
from .models import User
oauth2=OAuth2PasswordBearer(tokenUrl="/v1/auth/login")
_ITERATIONS=310_000
def hash_password(password:str)->str:
    salt=secrets.token_bytes(16); digest=pbkdf2_hmac("sha256",password.encode(),salt,_ITERATIONS)
    return "pbkdf2_sha256$"+str(_ITERATIONS)+"$"+base64.urlsafe_b64encode(salt).decode()+"$"+base64.urlsafe_b64encode(digest).decode()
def verify_password(password:str,encoded:str)->bool:
    try:
        scheme,it,salt,digest=encoded.split("$")
        if scheme!="pbkdf2_sha256": return False
        actual=pbkdf2_hmac("sha256",password.encode(),base64.urlsafe_b64decode(salt),int(it))
        return compare_digest(base64.urlsafe_b64encode(actual).decode(),digest)
    except Exception: return False
def create_token(user:User)->str:
    now=datetime.now(timezone.utc)
    return jwt.encode({"sub":str(user.id),"tenant":str(user.tenant_id),"role":user.role,"iat":now,"exp":now+timedelta(hours=12)},settings.app_secret,algorithm="HS256")
async def current_user(token:str=Depends(oauth2))->User:
    try:
        payload=jwt.decode(token,settings.app_secret,algorithms=["HS256"]); uid=payload.get("sub")
        if not uid: raise ValueError()
    except (JWTError,ValueError): raise HTTPException(401,"Invalid or expired token",headers={"WWW-Authenticate":"Bearer"})
    async with SessionLocal() as db:
        user=await db.get(User,uid)
        if not user or not user.is_active: raise HTTPException(401,"Account inactive")
        return user
def tenant_access(tenant_id,user:User):
    if user.tenant_id != tenant_id: raise HTTPException(403,"Tenant access denied")
