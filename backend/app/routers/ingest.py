from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas import IngestPayload
from ..safety_engine import evaluate_safety
from ..models import Reading, Alert, Pool
from ..websocket import broadcast_to_pool
from ..ml.predict import get_recommendation

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

    # --- ML recommendation (only once we have enough data) ---
    all_recent = (
        db.query(Reading)
        .filter(Reading.pool_id == payload.pool_id)
        .order_by(Reading.created_at.desc())
        .limit(30)
        .all()
    )

    recommendation = {"action": "nominal", "urgency": "none",
                      "reason": "Collecting data — need 30 readings to activate ML."}

    if len(all_recent) >= 30:
        try:
            recommendation = get_recommendation(
                all_recent,
                {
                    "tds_current":              payload.tds,
                    "tds_sustained_hours":      0,
                    "interventions_last_7days": 0,
                    "days_since_water_change":  0,
                }
            )
        except Exception:
            pass  # never break ingestion because of ML failure

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
        "alerts": triggered_alerts,
        "recommendation": recommendation
    })

    return {"status": "ok", "reading_id": reading.id, "safety_status": safety_status}
