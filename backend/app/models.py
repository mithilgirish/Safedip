import uuid
from sqlalchemy import Column, String, Float, Boolean, Text, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from .database import Base

class Pool(Base):
    __tablename__ = "pools"
    id               = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pool_id          = Column(String, unique=True, nullable=False, index=True)
    name             = Column(String, nullable=False)
    device_id        = Column(String, nullable=False)

class Reading(Base):
    __tablename__ = "readings"
    id               = Column(Integer, primary_key=True, index=True)
    device_id        = Column(String, nullable=False)
    pool_id          = Column(String, ForeignKey("pools.pool_id"), nullable=False, index=True)
    temperature      = Column(Float, nullable=False)
    tds              = Column(Float, nullable=False)
    turbidity        = Column(Float, nullable=False)
    ph               = Column(Float, nullable=False)
    orp              = Column(Float, nullable=False)
    safety_status    = Column(String, nullable=False)
    created_at       = Column(DateTime(timezone=True), server_default=func.now(), index=True)

class Alert(Base):
    __tablename__ = "alerts"
    id               = Column(Integer, primary_key=True, index=True)
    pool_id          = Column(String, ForeignKey("pools.pool_id"), nullable=False, index=True)
    message          = Column(Text, nullable=False)
    severity         = Column(String, nullable=False)  # 'caution', 'unsafe'
    resolved         = Column(Boolean, default=False)
    created_at       = Column(DateTime(timezone=True), server_default=func.now())
