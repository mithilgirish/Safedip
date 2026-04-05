from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta, timezone

from ..database import get_db
from ..models import Reading, Alert, Pool
from ..ml.predict import get_recommendation

router = APIRouter()


def _build_context(pool_id: str, db: Session, current_tds: float) -> dict:
    """
    Builds the context dict the decision layer needs.
    Queries the DB for intervention history and TDS sustained hours.
    """

    # --- How long has TDS been above 1500 ppm? ---
    tds_threshold = 1500.0
    # Walk back through readings until TDS drops below threshold
    recent = (
        db.query(Reading)
        .filter(Reading.pool_id == pool_id)
        .order_by(Reading.created_at.desc())
        .limit(5000)   # look back up to ~41 hrs at 30s intervals
        .all()
    )

    tds_sustained_hours = 0.0
    for r in recent:
        if r.tds > tds_threshold:
            tds_sustained_hours += 30 / 3600  # each reading = 30 seconds
        else:
            break  # first reading below threshold — stop counting

    # --- Chemical interventions in last 7 days ---
    seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
    interventions_7d = (
        db.query(Alert)
        .filter(
            Alert.pool_id  == pool_id,
            Alert.created_at >= seven_days_ago,
            Alert.severity.in_(["caution", "unsafe"]),
        )
        .count()
    )

    # --- Days since last water change ---
    # We track this via a special alert message convention
    # If no water change alert exists, default to 0
    last_change = (
        db.query(Alert)
        .filter(
            Alert.pool_id == pool_id,
            Alert.message.ilike("%water change%"),
        )
        .order_by(Alert.created_at.desc())
        .first()
    )

    if last_change and last_change.created_at:
        created_at = last_change.created_at
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)
        days_since_change = (datetime.now(timezone.utc) - created_at).days
    else:
        days_since_change = 0

    return {
        "tds_current":              current_tds,
        "tds_sustained_hours":      round(tds_sustained_hours, 2),
        "interventions_last_7days": interventions_7d,
        "days_since_water_change":  days_since_change,
    }


@router.post("/recommend/{pool_id}")
def get_pool_recommendation(pool_id: str, db: Session = Depends(get_db)):
    """
    POST /api/v1/recommend/{pool_id}

    Fetches the last 30 readings for the pool, runs them through
    the LSTM forecaster and decision layer, and returns a
    maintenance recommendation.
    """

    # --- Verify pool exists ---
    pool = db.query(Pool).filter(Pool.pool_id == pool_id).first()
    if not pool:
        raise HTTPException(
            status_code=404,
            detail=f"Pool '{pool_id}' not found."
        )

    # --- Fetch last 30 readings (newest first) ---
    recent_readings = (
        db.query(Reading)
        .filter(Reading.pool_id == pool_id)
        .order_by(Reading.created_at.desc())
        .limit(30)
        .all()
    )

    if len(recent_readings) < 30:
        raise HTTPException(
            status_code=422,
            detail=f"Not enough data yet. Need 30 readings, "
                   f"currently have {len(recent_readings)}. "
                   f"Keep the ESP32 running and try again shortly."
        )

    # --- Build context from DB ---
    current_tds = recent_readings[0].tds
    context     = _build_context(pool_id, db, current_tds)

    # --- Run ML pipeline ---
    try:
        recommendation = get_recommendation(recent_readings, context)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"ML inference failed: {str(e)}"
        )

    # --- Return full response ---
    return {
        "pool_id":        pool_id,
        "pool_name":      pool.name,
        "evaluated_at":   datetime.now(timezone.utc).isoformat(),
        "context":        context,
        "recommendation": recommendation,
    }