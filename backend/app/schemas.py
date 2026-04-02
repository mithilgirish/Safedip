from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID

class IngestPayload(BaseModel):
    device_id:   str
    pool_id:     str
    temperature: float
    tds:         float
    turbidity:   float
    ph:          float
    orp:         float

class ReadingResponse(BaseModel):
    id:            int
    device_id:     str
    pool_id:       str
    temperature:   float
    tds:           float
    turbidity:     float
    ph:            float
    orp:           float
    safety_status: str
    created_at:    datetime

    class Config:
        from_attributes = True

class AlertResponse(BaseModel):
    id:         int
    pool_id:    str
    message:    str
    severity:   str
    resolved:   bool
    created_at: datetime

    class Config:
        from_attributes = True

class PoolResponse(BaseModel):
    pool_id:        str
    name:           str
    device_id:      str
    latest_status:  Optional[str] = None

    class Config:
        from_attributes = True

class PoolCreate(BaseModel):
    pool_id:   str
    name:      str
    device_id: str
