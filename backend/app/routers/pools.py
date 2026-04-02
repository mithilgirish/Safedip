from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas import PoolResponse, PoolCreate
from ..models import Pool, Reading
from sqlalchemy import func

router = APIRouter()

@router.get("/pools", response_model=list[PoolResponse])
def get_all_pools(db: Session = Depends(get_db)):
    pools = db.query(Pool).all()
    
    results = []
    for pool in pools:
        # Get latest safety status
        latest_reading = db.query(Reading).filter(Reading.pool_id == pool.pool_id).order_by(Reading.created_at.desc()).first()
        status = latest_reading.safety_status if latest_reading else "unknown"
        
        results.append({
            "pool_id": pool.pool_id,
            "name": pool.name,
            "device_id": pool.device_id,
            "latest_status": status
        })
        
    return results

@router.post("/pools", status_code=201)
def create_pool(pool_data: PoolCreate, db: Session = Depends(get_db)):
    # Check if pool_id already exists
    existing = db.query(Pool).filter(Pool.pool_id == pool_data.pool_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Pool ID already exists")
    
    new_pool = Pool(**pool_data.dict())
    db.add(new_pool)
    db.commit()
    db.refresh(new_pool)
    return new_pool
