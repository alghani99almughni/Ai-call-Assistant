import uuid
from datetime import datetime
from sqlalchemy import String,Text,DateTime,JSON,func,Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped,mapped_column
from pgvector.sqlalchemy import Vector
from .db import Base
class Tenant(Base):
 __tablename__="tenants"
 id:Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
 name:Mapped[str]=mapped_column(String(180));slug:Mapped[str]=mapped_column(String(100),unique=True,index=True)
 industry:Mapped[str]=mapped_column(String(60),default="general");created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now())
class User(Base):
 __tablename__="users"
 id:Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4);tenant_id:Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),index=True)
 email:Mapped[str]=mapped_column(String(255),unique=True,index=True);password_hash:Mapped[str]=mapped_column(String(255));role:Mapped[str]=mapped_column(String(30),default="admin")
 is_active:Mapped[bool]=mapped_column(Boolean,default=True);created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now())
class TenantPhone(Base):
 __tablename__="tenant_phones"
 id:Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4);tenant_id:Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),index=True,unique=True)
 phone_number:Mapped[str]=mapped_column(String(20),unique=True,index=True);provider:Mapped[str]=mapped_column(String(30),default="twilio")
 provider_number_sid:Mapped[str|None]=mapped_column(String(64),nullable=True);enabled:Mapped[bool]=mapped_column(Boolean,default=True);created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now())
class CallSession(Base):
 __tablename__="call_sessions"
 id:Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4);tenant_id:Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),index=True)
 caller_number:Mapped[str|None]=mapped_column(String(40),nullable=True);status:Mapped[str]=mapped_column(String(20),default="active");summary:Mapped[str|None]=mapped_column(Text,nullable=True)
 started_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now());ended_at:Mapped[datetime|None]=mapped_column(DateTime(timezone=True),nullable=True)
class CallMessage(Base):
 __tablename__="call_messages"
 id:Mapped[int]=mapped_column(primary_key=True,autoincrement=True);tenant_id:Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),index=True);session_id:Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),index=True)
 role:Mapped[str]=mapped_column(String(20));content:Mapped[str]=mapped_column(Text);created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now())
class KnowledgeChunk(Base):
 __tablename__="knowledge_chunks"
 id:Mapped[int]=mapped_column(primary_key=True,autoincrement=True);tenant_id:Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),index=True);source_name:Mapped[str]=mapped_column(String(255));content:Mapped[str]=mapped_column(Text)
 embedding:Mapped[list|None]=mapped_column(Vector(384),nullable=True);metadata_json:Mapped[dict]=mapped_column("metadata",JSON,default=dict);created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now())
