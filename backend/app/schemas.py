from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
class TenantCreate(BaseModel):
    name:str=Field(min_length=2,max_length=180)
    slug:str=Field(pattern=r"^[a-z0-9-]{2,100}$")
    industry:str="general"
class TenantOut(BaseModel):
    id:UUID; name:str; slug:str; industry:str
    class Config: from_attributes=True
class CallOut(BaseModel):
    id:UUID; caller_number:str|None; status:str; summary:str|None; started_at:datetime
    class Config: from_attributes=True
class MessageIn(BaseModel):
    role:str="user"
    content:str=Field(min_length=1,max_length=8000)
class KnowledgeIn(BaseModel):
    source_name:str=Field(min_length=1,max_length=255)
    content:str=Field(min_length=20,max_length=100000)
