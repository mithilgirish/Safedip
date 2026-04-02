from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas import ReadingResponse
from ..models import Reading
from typing import List

router = APIRouter()

@router.get("/readings/{pool_id}", response_model=List[ReadingResponse])
def get_readings(pool_id: str, limit: int = 40, db: Session = Depends(get_db)):
    readings = db.query(Reading).filter(Reading.pool_id == pool_id).order_by(Reading.created_at.desc()).limit(limit).all()
    return readings
