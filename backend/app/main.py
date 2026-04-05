from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import ingest, pools, readings, alerts, recommend
from .websocket import router as ws_router
from .database import engine, Base

# Create database tables (Simplified for base version without Alembic setup initially)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="SafeDip API", version="1.0.0")

# CRITICAL: Allow Next.js frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(ingest.router,   prefix="/api/v1", tags=["Data Ingestion"])
app.include_router(pools.router,    prefix="/api/v1", tags=["Pool Management"])
app.include_router(readings.router, prefix="/api/v1", tags=["Readings"])
app.include_router(alerts.router,   prefix="/api/v1", tags=["Alerts"])
app.include_router(recommend.router, prefix="/api/v1", tags=["ML Recommendations"])
app.include_router(ws_router, tags=["WebSockets"])

@app.get("/")
def read_root():
    return {"message": "SafeDip API is active", "docs": "/docs"}
