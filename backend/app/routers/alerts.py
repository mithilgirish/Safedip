from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas import AlertResponse
from ..models import Alert
from typing import List

router = APIRouter()

@router.get("/alerts/{pool_id}", response_model=List[AlertResponse])
def get_alerts(pool_id: str, resolved: bool = False, db: Session = Depends(get_db)):
    alerts = db.query(Alert).filter(Alert.pool_id == pool_id, Alert.resolved == resolved).order_by(Alert.created_at.desc()).all()
    return alerts

@router.patch("/alerts/{alert_id}/resolve", response_model=AlertResponse)
def resolve_alert(alert_id: int, db: Session = Depends(get_db)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert.resolved = True
    db.commit()
    db.refresh(alert)
    return alert
