from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas import IngestPayload
from ..safety_engine import evaluate_safety
from ..models import Reading, Alert, Pool
from ..websocket import broadcast_to_pool

router = APIRouter()

@router.post("/ingest", status_code=201)
async def ingest_reading(payload: IngestPayload, db: Session = Depends(get_db)):
    # Verify pool exists
    pool = db.query(Pool).filter(Pool.pool_id == payload.pool_id).first()
    if not pool:
        # For base-laying version, let's auto-create pool if it doesn't exist?
        # Or return 404. Let's return 404 but provide a way to seed pools later.
        raise HTTPException(status_code=404, detail=f"Pool {payload.pool_id} not found")

    # Step 1: Run the safety threshold engine
    safety_status, alert_messages = evaluate_safety(payload)

    # Step 2: Persist the reading
    reading = Reading(**payload.dict(), safety_status=safety_status)
    db.add(reading)

    # Step 3: Persist alerts if triggered
    triggered_alerts = []
    for msg, severity in alert_messages:
        alert = Alert(pool_id=payload.pool_id, message=msg, severity=severity)
        db.add(alert)
        triggered_alerts.append({"message": msg, "severity": severity})

    db.commit()
    db.refresh(reading)

    # Step 4: Broadcast via WebSocket
    await broadcast_to_pool(payload.pool_id, {
        "type": "new_reading",
        "reading": {
            "id": reading.id,
            "device_id": reading.device_id,
            "pool_id": reading.pool_id,
            "temperature": reading.temperature,
            "tds": reading.tds,
            "turbidity": reading.turbidity,
            "ph": reading.ph,
            "orp": reading.orp,
            "safety_status": reading.safety_status,
            "created_at": reading.created_at.isoformat() if reading.created_at else None
        },
        "alerts": triggered_alerts
    })

    return {"status": "ok", "reading_id": reading.id, "safety_status": safety_status}
