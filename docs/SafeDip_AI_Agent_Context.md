# SafeDip: AI-Driven IoT Swimming Pool Safety Monitoring System
## Complete AI Agent Build Context & Reference Document

> **Purpose:** This document is the single source of truth for an AI coding agent to build the SafeDip platform end-to-end. It consolidates the Project Documentation, Business Requirements Document (BRD), and technical system context into one comprehensive reference. Read this document fully before writing a single line of code.

---

## Table of Contents

1. [Project Overview & Vision](#1-project-overview--vision)
2. [Business Context & Stakeholders](#2-business-context--stakeholders)
3. [System Architecture](#3-system-architecture)
4. [Tech Stack Specification](#4-tech-stack-specification)
5. [Directory Structure](#5-directory-structure)
6. [Database Schema (PostgreSQL)](#6-database-schema-postgresql)
7. [Hardware Edge Node (ESP32)](#7-hardware-edge-node-esp32)
8. [Backend — FastAPI](#8-backend--fastapi)
9. [Frontend — Next.js](#9-frontend--nextjs)
10. [Safety Threshold Engine](#10-safety-threshold-engine)
11. [Real-Time System (WebSockets)](#11-real-time-system-websockets)
12. [AI & Predictive Analytics Layer](#12-ai--predictive-analytics-layer)
13. [Wearable PWA Interface](#13-wearable-pwa-interface)
14. [Business Rules & Constraints](#14-business-rules--constraints)
15. [Non-Functional Requirements](#15-non-functional-requirements)
16. [Risk Register & Mitigations](#16-risk-register--mitigations)
17. [Execution Directives for the AI Agent](#17-execution-directives-for-the-ai-agent)
18. [User Ecosystem & Allergy Logic](#18-user-ecosystem--allergy-logic)

---

## 1. Project Overview & Vision

### 1.1 What is SafeDip?

SafeDip is a **commercial-grade, end-to-end IoT water safety and compliance platform** for the recreational water industry. It replaces manual, labor-intensive water testing with a continuous, real-time telemetry pipeline.

The system pairs an **ESP32 hardware edge node** with a **FastAPI/Next.js full-stack backend** and a **PostgreSQL database** to deliver:

- **Personalized safety alerts** pushed directly to swimmers via a wearable Progressive Web App (PWA).
- **Comprehensive analytical dashboards** for facility administrators.
- **Automated compliance logging** replacing paper-based maintenance records.
- **Predictive maintenance insights** powered by ML on historical time-series data.

### 1.2 Core Problem Being Solved

| Problem | Impact |
|---|---|
| Manual water testing is infrequent, inconsistent, and time-delayed | Chemical imbalances go unnoticed for up to 4 hours |
| No real-time swimmer awareness | Users have zero visibility into water safety at the moment of entry |
| Poor water chemistry (pH, chlorine depletion) | Skin irritation, eye infections, recreational water illnesses (RWIs) |
| No immutable digital records | Facilities struggle to prove compliance during health inspections or lawsuits |

### 1.3 The SafeDip Shift

> **From:** Reactive pool maintenance (test → find problem → react)
> **To:** Proactive personal safety (continuous monitoring → predict → prevent)

The system targets **B2B buyers** (facility managers, pool operators, hotel chains, apartment complexes) while delivering a **B2C experience** to end-users (swimmers).

---

## 2. Business Context & Stakeholders

### 2.1 Stakeholder Profiles

| Stakeholder | Role & Motivation | Key Need from SafeDip |
|---|---|---|
| **Facility Manager / Buyer** | Accountable for budget and legal compliance | Automated digital compliance logs, reduced labor costs, lawsuit risk mitigation |
| **Maintenance Operator** | Performs daily physical upkeep | Immediate drift alerts enabling targeted maintenance instead of blind testing |
| **Health Inspector** | Audits commercial facilities against regulations | Tamper-proof, exportable historical data proving compliance with safety standards |
| **Swimmer (End-User)** | Pays to use the facility | Real-time water safety assurance via wearable interface |

### 2.2 Business Objectives

**OBJ-01:** Reduce time between a chemical imbalance occurring and facility manager notification from ~4 hours to **under 10 seconds**.

**OBJ-02:** Automate **100%** of compliance logging, eliminating paper-based maintenance records.

**OBJ-03:** Support multi-facility management — a single regional manager must be able to monitor **up to 50 distinct pools** from one central dashboard.

### 2.3 Key Performance Indicators (KPIs)

| KPI | Target |
|---|---|
| Adoption KPI | Pilot deployments in ≥ 3 distinct commercial settings (1 hotel, 1 public pool, 1 apartment complex) |
| System Uptime KPI | 99.5% availability for the cloud dashboard and alert engine |
| Labor ROI KPI | ≥ 75% reduction in manual water testing hours per deployed facility |

### 2.4 Revenue Model (Hardware-Enabled SaaS)

**Tier 1 — Hardware Acquisition Fee:** One-time upfront cost for the physical sensor kit + installation.

**Tier 2 — Monthly Platform Subscription (SaaS):** Recurring monthly fee per pool. Covers cloud hosting, multi-pool dashboard access, automated compliance reporting, and the predictive AI analytics engine.

**Estimated COGS per hardware kit: ₹13,960 – ₹14,460**

---

## 3. System Architecture

SafeDip runs on a **decoupled, multi-tenant, 4-tier architecture** designed to support multiple physical pools simultaneously.

```
┌──────────────────────────────────────────────────────────────────────┐
│                         SAFEDIP ARCHITECTURE                         │
│                                                                      │
│  ┌─────────────┐    HTTP POST     ┌──────────────────────────────┐   │
│  │  TIER 1     │ ──────────────►  │         TIER 2               │   │
│  │  ESP32      │                  │    FastAPI Backend           │   │
│  │  Edge Node  │                  │  ┌──────────────────────┐    │   │
│  │             │                  │  │ Safety Threshold     │    │   │
│  │ Sensors:    │                  │  │ Engine               │    │   │
│  │  - pH       │                  │  │ (SAFE/CAUTION/UNSAFE)│    │   │
│  │  - TDS      │                  │  └──────────────────────┘    │   │
│  │  - ORP      │                  │  ┌──────────────────────┐    │   │
│  │  - Turbidity│                  │  │ Alert Generator      │    │   │
│  │  - Temp     │                  │  └──────────────────────┘    │   │
│  └─────────────┘                  └──────────────┬───────────────┘   │
│                                                  │                   │
│                                           SQL Write                  │
│                                                  ▼                   │
│                                   ┌──────────────────────────────┐   │
│                                   │         TIER 3               │   │
│                                   │    PostgreSQL Database       │   │
│                                   │  (Supabase / Local)          │   │
│                                   │  tables: pools, readings,    │   │
│                                   │          alerts              │   │
│                                   └──────────────┬───────────────┘   │
│                                                  │                   │
│                                    WebSocket Broadcast               │
│                                                  ▼                   │
│                                   ┌──────────────────────────────┐   │
│                                   │         TIER 4               │   │
│                                   │  Presentation Layer          │   │
│                         ┌─────────┤  ┌────────────┐ ┌─────────┐ │   │
│                         │         │  │ Admin      │ │Wearable │ │   │
│                         │         │  │ Dashboard  │ │PWA      │ │   │
│                         │         │  │ (Next.js)  │ │(Watch)  │ │   │
│                         │         │  └────────────┘ └─────────┘ │   │
│                         │         └──────────────────────────────┘   │
└─────────────────────────┴────────────────────────────────────────────┘
```

### 3.1 Tier 1 — Hardware / Edge Node (ESP32)

- **Processor:** ESP32 Microcontroller (C++ / Arduino Framework)
- **Sensors:** pH probe (analog + amplifier), TDS Gravity analog, Turbidity SEN0189, ORP Grove ORP Pro, DS18B20 waterproof temperature probe
- **Operation:**
  1. Reads analog sensor data
  2. Applies **15-sample noise-reduction averaging** per sensor
  3. Dynamically **temperature-compensates the TDS reading**
  4. Formats a JSON payload
  5. Transmits via **HTTP POST over Wi-Fi**

### 3.2 Tier 2 — Backend API & Logic Layer (FastAPI)

- Receives edge payload, validates device credentials
- Runs the **Safety Threshold Matrix** (see Section 10)
- Categorizes reading as `SAFE`, `CAUTION`, or `UNSAFE`
- Writes data to PostgreSQL
- Broadcasts WebSocket event to connected frontend clients

### 3.3 Tier 3 — Database Layer (PostgreSQL)

- **Cloud:** Supabase (managed PostgreSQL)
- **Offline/Air-gapped:** Local SQLite via Prisma ORM
- Stores relational metadata (pool registry) and high-velocity time-series telemetry
- Utilizes WebSockets for real-time data broadcasting

### 3.4 Tier 4 — Presentation & UI Layer

- **Admin Dashboard:** Next.js (App Router), Tailwind CSS, Recharts — real-time metrics, historical trends, active alert feed
- **Wearable Interface:** Hyper-minimalist PWA for smartwatches — subscribes to real-time DB updates and triggers **HTML5 Vibration API** on `UNSAFE` status

---

## 4. Tech Stack Specification

### Backend

| Component | Technology |
|---|---|
| Framework | FastAPI (Python 3.10+) |
| ORM | SQLAlchemy or SQLModel |
| Database | PostgreSQL (Supabase cloud or local) |
| Migrations | Alembic |
| Real-time | FastAPI native WebSocket endpoints |
| Language | Python 3.10+ |

### Frontend

| Component | Technology |
|---|---|
| Framework | Next.js (App Router, React 18) |
| Styling | Tailwind CSS |
| Charts | Recharts |
| Icons | Lucide-React |
| Data Fetching | SWR or `useEffect` + WebSocket |
| Wearable UI | Progressive Web App (PWA) |

### Hardware

| Component | Technology |
|---|---|
| Microcontroller | ESP32 |
| Language | C++ / Arduino Framework |
| Payload | `application/json` via HTTP POST |

---

## 5. Directory Structure

The agent **must** maintain strict separation between backend and frontend:

```
safedip/
├── backend/                        # FastAPI Python application
│   ├── alembic/                    # Database migration scripts
│   │   └── versions/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI app entry point, CORS config
│   │   ├── database.py             # SQLAlchemy engine & session
│   │   ├── models.py               # ORM models (Pool, Reading, Alert)
│   │   ├── schemas.py              # Pydantic request/response schemas
│   │   ├── routers/
│   │   │   ├── ingest.py           # POST /api/v1/ingest
│   │   │   ├── pools.py            # GET /api/v1/pools
│   │   │   ├── readings.py         # GET /api/v1/readings/{pool_id}
│   │   │   └── alerts.py           # GET /api/v1/alerts/{pool_id}
│   │   ├── websocket.py            # WS /ws/pool/{pool_id}
│   │   └── safety_engine.py        # Threshold evaluation logic
│   ├── requirements.txt
│   └── alembic.ini
│
├── frontend/                       # Next.js application
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx                # Admin dashboard root
│   │   └── watch/
│   │       └── page.tsx            # Wearable PWA root
│   ├── components/
│   │   ├── SafetyBanner.tsx
│   │   ├── MetricsGrid.tsx
│   │   ├── MetricCard.tsx
│   │   ├── HistoricalChart.tsx
│   │   ├── AlertsFeed.tsx
│   │   └── PoolSelector.tsx
│   ├── hooks/
│   │   └── usePoolWebSocket.ts     # WebSocket connection hook
│   ├── lib/
│   │   └── api.ts                  # API call functions
│   ├── public/
│   │   └── manifest.json           # PWA manifest
│   ├── tailwind.config.ts
│   └── package.json
│
└── hardware/
    └── esp32_firmware/
        └── safedip_node.ino        # ESP32 C++ sketch
```

---

## 6. Database Schema (PostgreSQL)

The agent must implement this schema via **Alembic migrations** — no mock data, no manual SQL execution.

### 6.1 Table: `pools` (Registry)

Registers physical pool locations and binds them to specific ESP32 hardware kits.

```sql
CREATE TABLE pools (
    id          UUID            PRIMARY KEY DEFAULT gen_random_uuid(),
    pool_id     VARCHAR         UNIQUE NOT NULL,   -- e.g., 'pool_vit_01'
    name        VARCHAR         NOT NULL,          -- e.g., 'Main Campus Pool'
    device_id   VARCHAR         NOT NULL           -- Bound ESP32 MAC/ID
);
```

### 6.2 Table: `readings` (Telemetry)

High-velocity time-series data. **Must be indexed on `pool_id` and `created_at`.**

```sql
CREATE TABLE readings (
    id              BIGSERIAL       PRIMARY KEY,
    device_id       VARCHAR         NOT NULL,
    pool_id         VARCHAR         NOT NULL REFERENCES pools(pool_id),
    temperature     REAL            NOT NULL,   -- °C
    tds             REAL            NOT NULL,   -- ppm (Total Dissolved Solids)
    turbidity       REAL            NOT NULL,   -- NTU
    ph              REAL            NOT NULL,   -- 0–14 scale
    orp             REAL            NOT NULL,   -- mV (Oxidation Reduction Potential)
    safety_status   VARCHAR         NOT NULL,   -- Enum: 'safe' | 'caution' | 'unsafe'
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_readings_pool_time ON readings (pool_id, created_at DESC);
```

### 6.3 Table: `alerts` (Event Logs)

Auto-generated when any parameter breaches its threshold.

```sql
CREATE TABLE alerts (
    id          BIGSERIAL       PRIMARY KEY,
    pool_id     VARCHAR         NOT NULL REFERENCES pools(pool_id),
    message     TEXT            NOT NULL,   -- e.g., "pH 8.1 exceeds safe limit."
    severity    VARCHAR         NOT NULL,   -- Enum: 'caution' | 'unsafe'
    resolved    BOOLEAN         NOT NULL DEFAULT FALSE,
    created_at  TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);
```

### 6.4 SQLAlchemy ORM Models (Python)

```python
# app/models.py
import uuid
from sqlalchemy import Column, String, Float, Boolean, Text, BigInteger, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from .database import Base

class Pool(Base):
    __tablename__ = "pools"
    id        = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pool_id   = Column(String, unique=True, nullable=False)
    name      = Column(String, nullable=False)
    device_id = Column(String, nullable=False)

class Reading(Base):
    __tablename__ = "readings"
    id            = Column(BigInteger, primary_key=True, autoincrement=True)
    device_id     = Column(String, nullable=False)
    pool_id       = Column(String, nullable=False)   # FK to pools.pool_id
    temperature   = Column(Float, nullable=False)
    tds           = Column(Float, nullable=False)
    turbidity     = Column(Float, nullable=False)
    ph            = Column(Float, nullable=False)
    orp           = Column(Float, nullable=False)
    safety_status = Column(String, nullable=False)
    created_at    = Column(DateTime(timezone=True), server_default=func.now())

class Alert(Base):
    __tablename__ = "alerts"
    id         = Column(BigInteger, primary_key=True, autoincrement=True)
    pool_id    = Column(String, nullable=False)      # FK to pools.pool_id
    message    = Column(Text, nullable=False)
    severity   = Column(String, nullable=False)
    resolved   = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

---

## 7. Hardware Edge Node (ESP32)

### 7.1 Bill of Materials

| Component | Purpose / Specification |
|---|---|
| ESP32 | Central processing and Wi-Fi transmission |
| ORP Sensor | Grove ORP Pro — disinfection effectiveness |
| pH Sensor | Analog probe + amplifier |
| Turbidity Sensor | SEN0189 or equivalent — water clarity |
| TDS Sensor | Gravity analog — dissolved impurities |
| DS18B20 | Waterproof temperature probe |
| Misc. | Dupont cables, 5V power adapter, waterproof enclosure |

### 7.2 ESP32 Firmware Logic

```cpp
// safedip_node.ino — Simplified pseudocode for agent reference

const char* WIFI_SSID     = "YOUR_SSID";
const char* WIFI_PASS     = "YOUR_PASSWORD";
const char* API_ENDPOINT  = "http://<BACKEND_HOST>/api/v1/ingest";
const char* DEVICE_ID     = "ESP32_01";
const char* POOL_ID       = "pool_vit_01";

// --- Noise Reduction ---
// For each sensor, take 15 samples and return the average
float readAveraged(int pin, int samples = 15) {
    float total = 0;
    for (int i = 0; i < samples; i++) {
        total += analogRead(pin);
        delay(10);
    }
    return total / samples;
}

// --- Temperature Compensation for TDS ---
// Raw TDS must be corrected using current water temperature
float compensateTDS(float rawTDS, float tempC) {
    float compensationCoeff = 1.0 + 0.02 * (tempC - 25.0);
    return rawTDS / compensationCoeff;
}

void loop() {
    float temp    = readTemperatureDS18B20();
    float ph      = mapRawToPH(readAveraged(PH_PIN));
    float tds_raw = mapRawToTDS(readAveraged(TDS_PIN));
    float tds     = compensateTDS(tds_raw, temp);
    float turb    = mapRawToNTU(readAveraged(TURB_PIN));
    float orp     = mapRawToMV(readAveraged(ORP_PIN));

    // --- Build JSON Payload ---
    String payload = "{";
    payload += "\"device_id\":\"" + String(DEVICE_ID) + "\",";
    payload += "\"pool_id\":\"" + String(POOL_ID) + "\",";
    payload += "\"temperature\":" + String(temp, 2) + ",";
    payload += "\"tds\":" + String(tds, 2) + ",";
    payload += "\"turbidity\":" + String(turb, 2) + ",";
    payload += "\"ph\":" + String(ph, 2) + ",";
    payload += "\"orp\":" + String(orp, 2);
    payload += "}";

    // HTTP POST to FastAPI backend
    HTTPClient http;
    http.begin(API_ENDPOINT);
    http.addHeader("Content-Type", "application/json");
    http.POST(payload);
    http.end();

    delay(5000);  // Transmit every 5 seconds
}
```

---

## 8. Backend — FastAPI

### 8.1 Application Entry Point & CORS

```python
# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import ingest, pools, readings, alerts
from .websocket import router as ws_router

app = FastAPI(title="SafeDip API", version="1.0.0")

# CRITICAL: Allow Next.js frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ingest.router,   prefix="/api/v1")
app.include_router(pools.router,    prefix="/api/v1")
app.include_router(readings.router, prefix="/api/v1")
app.include_router(alerts.router,   prefix="/api/v1")
app.include_router(ws_router)
```

### 8.2 Pydantic Schemas

```python
# app/schemas.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

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
```

### 8.3 Ingestion Endpoint

```python
# app/routers/ingest.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas import IngestPayload
from ..safety_engine import evaluate_safety
from ..models import Reading, Alert
from ..websocket import broadcast_to_pool

router = APIRouter()

@router.post("/ingest", status_code=201)
async def ingest_reading(payload: IngestPayload, db: Session = Depends(get_db)):
    # Step 1: Run the safety threshold engine
    safety_status, alert_messages = evaluate_safety(payload)

    # Step 2: Persist the reading
    reading = Reading(**payload.dict(), safety_status=safety_status)
    db.add(reading)

    # Step 3: Persist alerts if triggered
    for msg, severity in alert_messages:
        alert = Alert(pool_id=payload.pool_id, message=msg, severity=severity)
        db.add(alert)

    db.commit()
    db.refresh(reading)

    # Step 4: Broadcast via WebSocket to connected frontend clients
    await broadcast_to_pool(payload.pool_id, {
        "type": "new_reading",
        "reading": reading.__dict__,
        "alerts": [{"message": m, "severity": s} for m, s in alert_messages]
    })

    return {"status": "ok", "reading_id": reading.id, "safety_status": safety_status}
```

### 8.4 Retrieval Endpoints

```python
# app/routers/pools.py
@router.get("/pools")
def get_all_pools(db: Session = Depends(get_db)):
    # Returns all pools with their most recent safety_status

# app/routers/readings.py
@router.get("/readings/{pool_id}")
def get_readings(pool_id: str, limit: int = 40, db: Session = Depends(get_db)):
    # Returns last `limit` readings for Recharts historical visualization

# app/routers/alerts.py
@router.get("/alerts/{pool_id}")
def get_alerts(pool_id: str, resolved: bool = False, db: Session = Depends(get_db)):
    # Returns active (unresolved) alerts for the dashboard alert feed
```

### 8.5 WebSocket Endpoint

```python
# app/websocket.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, List
import json

router = APIRouter()

# Connection manager: maintains a map of pool_id -> list of active WebSocket connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, pool_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.setdefault(pool_id, []).append(websocket)

    def disconnect(self, pool_id: str, websocket: WebSocket):
        if pool_id in self.active_connections:
            self.active_connections[pool_id].remove(websocket)

    async def broadcast(self, pool_id: str, data: dict):
        for ws in self.active_connections.get(pool_id, []):
            await ws.send_json(data)

manager = ConnectionManager()

async def broadcast_to_pool(pool_id: str, data: dict):
    await manager.broadcast(pool_id, data)

@router.websocket("/ws/pool/{pool_id}")
async def websocket_endpoint(websocket: WebSocket, pool_id: str):
    await manager.connect(pool_id, websocket)
    try:
        while True:
            await websocket.receive_text()  # Keep connection alive
    except WebSocketDisconnect:
        manager.disconnect(pool_id, websocket)
```

---

## 9. Frontend — Next.js

### 9.1 Overall Layout & State Model

- A **global `PoolSelector` dropdown** in the top navigation allows switching pool context (`pool_id`).
- An **active WebSocket connection** is maintained per selected `pool_id`.
- On pool switch, the WebSocket disconnects from the old pool and connects to the new one.
- All state derives from the WebSocket stream + initial REST fetch on mount.

### 9.2 Core Dashboard Components

#### `SafetyBanner`

Full-width banner reflecting the current pool safety state.

| Status | Background Color | Message |
|---|---|---|
| `safe` | Emerald (`bg-emerald-500`) | "All parameters nominal." |
| `caution` | Amber (`bg-amber-500`) | "Caution: Parameters nearing limits." |
| `unsafe` | Red pulsing (`bg-red-600 animate-pulse`) | "UNSAFE: Evacuate pool immediately." |

```tsx
// components/SafetyBanner.tsx
type Status = 'safe' | 'caution' | 'unsafe'

const statusConfig = {
  safe:    { bg: 'bg-emerald-500', text: 'All parameters nominal.' },
  caution: { bg: 'bg-amber-500',   text: 'Caution: Parameters nearing limits.' },
  unsafe:  { bg: 'bg-red-600 animate-pulse', text: 'UNSAFE: Evacuate pool immediately.' },
}

export function SafetyBanner({ status }: { status: Status }) {
  const config = statusConfig[status]
  return (
    <div className={`w-full py-4 px-6 text-white text-center text-xl font-bold ${config.bg}`}>
      {config.text}
    </div>
  )
}
```

#### `MetricsGrid`

A responsive CSS grid of 5 `MetricCard` components, one per sensor parameter.

```tsx
// components/MetricsGrid.tsx
// Renders: Temperature | pH | TDS | Turbidity | ORP
// Each card shows: current value, unit, parameter name, color-coded status badge
// Badge colors: green (safe), yellow (caution), red (unsafe)
// Status determined per-parameter using the Threshold Matrix (Section 10)
```

#### `MetricCard`

Individual card per parameter. Must evaluate its own status badge color independently from the global safety status.

```tsx
interface MetricCardProps {
  label:  string     // e.g., "pH"
  value:  number     // e.g., 7.35
  unit:   string     // e.g., "" | "°C" | "ppm" | "NTU" | "mV"
  status: 'safe' | 'caution' | 'unsafe'
}
```

#### `HistoricalChart`

A Recharts `LineChart` displaying the last 40 readings from `GET /api/v1/readings/{pool_id}?limit=40`.

- X-axis: `created_at` (timestamp)
- Y-axis: **toggleable** between the 5 parameters (toggle buttons above the chart)
- Each metric has its own Y-axis domain for readability
- Smooth line, dot on hover, responsive container

```tsx
const METRICS = [
  { key: 'temperature', label: 'Temperature', unit: '°C',  color: '#f97316' },
  { key: 'ph',          label: 'pH',          unit: '',    color: '#3b82f6' },
  { key: 'tds',         label: 'TDS',         unit: 'ppm', color: '#8b5cf6' },
  { key: 'turbidity',   label: 'Turbidity',   unit: 'NTU', color: '#06b6d4' },
  { key: 'orp',         label: 'ORP',         unit: 'mV',  color: '#10b981' },
]
```

#### `AlertsFeed`

Scrollable column showing unacknowledged records from `GET /api/v1/alerts/{pool_id}?resolved=false`.

- Each alert entry displays: severity badge (color-coded), message text, and relative timestamp.
- Severity `unsafe` → red badge, `caution` → amber badge.
- New alerts prepend to the top of the list.
- Each alert has a "Resolve" button that calls `PATCH /api/v1/alerts/{alert_id}/resolve`.

#### `PoolSelector`

Dropdown in top nav populated by `GET /api/v1/pools`. Switching pools triggers a new WebSocket connection and refetches all component data for the new pool context.

### 9.3 WebSocket Hook

```ts
// hooks/usePoolWebSocket.ts
import { useEffect, useRef, useState } from 'react'

export function usePoolWebSocket(poolId: string | null) {
  const [latestReading, setLatestReading] = useState(null)
  const [latestAlerts,  setLatestAlerts]  = useState([])
  const ws = useRef<WebSocket | null>(null)

  useEffect(() => {
    if (!poolId) return
    ws.current = new WebSocket(`ws://localhost:8000/ws/pool/${poolId}`)

    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data)
      if (data.type === 'new_reading') {
        setLatestReading(data.reading)
        if (data.alerts.length > 0) setLatestAlerts(prev => [...data.alerts, ...prev])
      }
    }

    return () => ws.current?.close()
  }, [poolId])

  return { latestReading, latestAlerts }
}
```

---

## 10. Safety Threshold Engine

This logic lives in `backend/app/safety_engine.py` and is invoked for **every single reading** before database insertion.

### 10.1 Threshold Matrix

| Parameter | Unit | Safe Range | Caution Range | Unsafe Condition |
|---|---|---|---|---|
| **pH** | — | 7.2 – 7.6 | 7.0 – 7.8 | `< 6.8` OR `> 8.0` |
| **TDS** | ppm | 0 – 500 | 0 – 1000 | `> 1000` |
| **Turbidity** | NTU | 0 – 50 | 0 – 100 | `> 100` |
| **Temperature** | °C | 26 – 32 | 20 – 35 | `< 18` OR `> 38` |
| **ORP** | mV | 650 – 750 | 600 – 800 | `< 550` OR `> 850` |

### 10.2 Evaluation Rules

```
1. IF ANY parameter is in the UNSAFE range:
       safety_status = 'unsafe'
       Generate an alert with severity = 'unsafe'

2. ELSE IF ANY parameter is in the CAUTION range:
       safety_status = 'caution'
       Generate an alert with severity = 'caution'

3. ELSE:
       safety_status = 'safe'
       No alert generated
```

### 10.3 Python Implementation

```python
# app/safety_engine.py
from typing import Tuple, List

def evaluate_safety(p) -> Tuple[str, List[Tuple[str, str]]]:
    """
    Returns (safety_status, [(alert_message, severity), ...])
    Evaluates all 5 parameters against the WHO-aligned threshold matrix.
    """
    unsafe_msgs  = []
    caution_msgs = []

    # pH
    if p.ph < 6.8 or p.ph > 8.0:
        unsafe_msgs.append((f"pH {p.ph:.2f} is outside safe limits (6.8–8.0).", "unsafe"))
    elif p.ph < 7.0 or p.ph > 7.8:
        caution_msgs.append((f"pH {p.ph:.2f} is approaching limits.", "caution"))

    # TDS
    if p.tds > 1000:
        unsafe_msgs.append((f"TDS {p.tds:.0f} ppm exceeds unsafe threshold (>1000 ppm).", "unsafe"))
    elif p.tds > 500:
        caution_msgs.append((f"TDS {p.tds:.0f} ppm is elevated.", "caution"))

    # Turbidity
    if p.turbidity > 100:
        unsafe_msgs.append((f"Turbidity {p.turbidity:.1f} NTU is unsafe (>100 NTU).", "unsafe"))
    elif p.turbidity > 50:
        caution_msgs.append((f"Turbidity {p.turbidity:.1f} NTU is elevated.", "caution"))

    # Temperature
    if p.temperature < 18 or p.temperature > 38:
        unsafe_msgs.append((f"Temperature {p.temperature:.1f}°C is outside safe range.", "unsafe"))
    elif p.temperature < 20 or p.temperature > 35:
        caution_msgs.append((f"Temperature {p.temperature:.1f}°C is approaching limits.", "caution"))

    # ORP
    if p.orp < 550 or p.orp > 850:
        unsafe_msgs.append((f"ORP {p.orp:.0f} mV is outside safe range (550–850 mV).", "unsafe"))
    elif p.orp < 600 or p.orp > 800:
        caution_msgs.append((f"ORP {p.orp:.0f} mV is approaching limits.", "caution"))

    if unsafe_msgs:
        return "unsafe", unsafe_msgs
    elif caution_msgs:
        return "caution", caution_msgs
    else:
        return "safe", []
```

---

## 11. Real-Time System (WebSockets)

### 11.1 Data Flow

```
ESP32 POST /api/v1/ingest
      ↓
FastAPI evaluates & writes to DB
      ↓
FastAPI calls broadcast_to_pool(pool_id, payload)
      ↓
WebSocket Manager sends JSON to all connected clients for that pool_id
      ↓
Next.js frontend receives message in usePoolWebSocket hook
      ↓
React state updates → SafetyBanner, MetricsGrid, AlertsFeed re-render
```

### 11.2 WebSocket Message Format (Backend → Frontend)

```json
{
  "type": "new_reading",
  "reading": {
    "id": 1042,
    "device_id": "ESP32_01",
    "pool_id": "pool_vit_01",
    "temperature": 28.5,
    "tds": 320.0,
    "turbidity": 12.4,
    "ph": 7.35,
    "orp": 695.0,
    "safety_status": "safe",
    "created_at": "2024-01-15T10:30:00Z"
  },
  "alerts": [
    {
      "message": "pH 8.1 exceeds safe limit.",
      "severity": "unsafe"
    }
  ]
}
```

---

## 12. AI & Predictive Analytics Layer

### 12.1 Current Phase (MVP)

The FastAPI backend provides native access to Python's full data science ecosystem. The current MVP uses **rule-based threshold classification** (Section 10) as the safety engine.

### 12.2 Future Phase (Predictive ML)

The historical time-series dataset from the `readings` table will be used to train and deploy predictive models directly on the FastAPI ingestion pipeline.

**Target Models:**

| Model | Purpose |
|---|---|
| **ARIMA** | Univariate time-series forecasting of pH, ORP, TDS trends |
| **LSTM (PyTorch)** | Multivariate sequence modeling — captures interaction between parameters |

**Prediction Target:** Forecast chemical degradation 30–60 minutes ahead, enabling pool operators to **preemptively balance water** before it breaches safe limits.

**Key Input Signal:** Rate of change in pH and ORP over rolling 15-minute windows.

**Libraries to integrate (future):** `scikit-learn`, `PyTorch`, `statsmodels`, `pandas`, `numpy`

**Integration point:** After `evaluate_safety()` in the ingestion pipeline, run a pre-loaded model's `.predict()` call and append forecast data to the WebSocket broadcast payload.

---

## 13. Wearable & Mobile PWA Ecosystem

SafeDip provides two distinct user-facing interfaces beyond the Admin Dashboard: a **Wearable PWA** for real-time swim-time alerts and a **Mobile User PWA** for public pool information and safety checks.

### 13.1 Wearable PWA (`/watch`)
- **Route**: `/watch`
- **Purpose**: Real-time safety monitoring on smartwatches.
- **Features**: High-contrast status indicator, vibration alerts on `UNSAFE` transitions.

### 13.2 Mobile User PWA (`/pool/[id]`)
- **Route**: `/pool/[pool_id]`
- **Purpose**: Public-facing view for swimmers to check water quality before entry.
- **QR Entry**: Users scan a physical QR code at the pool location, which deep-links directly to this route.
- **Personalized Alerts**: Shows safe/warning messages based on the user's specific sensitivity profile (stored in LocalStorage).

### 13.3 Allergy & Sensitivity Logic
Users can configure "Sensitivities" in the `/preferences` route. The frontend compares real-time readings against these thresholds:

| Sensitivity Type | Trigger Parameter | Warning Condition |
|---|---|---|
| **Sensitive Skin** | pH | pH < 7.0 or pH > 7.8 |
| **Eye Sensitivity** | ORP / Chlorine | ORP > 800mV or pH > 7.6 |
| **Respiratory** | TDS | TDS > 800 ppm |

---

## 14. Business Rules & Constraints

These are non-negotiable rules derived from the BRD that the agent must honor throughout implementation.

| Rule ID | Description |
|---|---|
| **BR-01** | The system must **continuously** gather data on pH, TDS, Turbidity, Temperature, and ORP. No parameter may be omitted. |
| **BR-02** | All historical water data must be stored in an **immutable format** and be easily exportable for health inspections. Do not allow DELETE on the `readings` table. |
| **BR-03** | Alerts must be triggered **automatically** the moment any parameter breaches a threshold. No batching or delay. |
| **BR-04** | Real-time visual AND physical (vibration) alerts must reach the swimmer's wearable device. |
| **BR-05** | The platform must support monitoring up to **50 distinct pools** from a single dashboard (multi-tenant architecture required). |
| **BR-06** | If Wi-Fi connectivity is lost, the ESP32 hardware must **buffer readings locally** and the dashboard must show a "Connection Lost" alert. |
| **BR-07** | Sensor recalibration must be **enforced via software every 30 days** to prevent false alert fatigue from calibration drift. |

---

## 15. Non-Functional Requirements

| Category | Requirement |
|---|---|
| **Availability** | 99.5% uptime for cloud dashboard and alert engine |
| **Latency** | End-to-end alert latency (sensor → wearable) must be under 10 seconds |
| **Scalability** | Architecture must support up to 50 pools without schema changes |
| **Security** | All API endpoints must validate `device_id` against the `pools` registry before processing |
| **Responsiveness** | All admin dashboard UI must be fully responsive (mobile, tablet, desktop) using Tailwind utility classes |
| **Exportability** | Historical readings must be exportable as CSV via an admin endpoint |
| **CORS** | FastAPI must be configured to accept requests from the Next.js localhost port (3000) and production domain |

---

## 16. Risk Register & Mitigations

| Risk | Business Impact | Mitigation Strategy |
|---|---|---|
| **Facility Wi-Fi Unreliability** | Loss of real-time monitoring and alert capabilities | Implement local data buffering on ESP32 SPIFFS storage; dashboard displays "Connection Lost" alert if ping drops |
| **Sensor Calibration Drift** | False positive alerts → "alert fatigue" for staff → ignored real alerts | Mandatory software-enforced recalibration routine every 30 days; stale calibration triggers dashboard warning |
| **Adoption Resistance** | Staff reject technology in favour of legacy paper methods | Design dashboard as hyper-intuitive; frame as staff empowerment tool, not surveillance |
| **Cloud Database Outage** | All monitoring halts; no historical data during downtime | Implement SQLite fallback for local/air-gapped deployments via Prisma ORM |

---

## 17. Execution Directives for the AI Agent

These directives are **mandatory instructions** the agent must follow during code generation:

### Architecture
- [ ] Strictly separate FastAPI (`/backend`) and Next.js (`/frontend`) into distinct directories.
- [ ] Never mix backend and frontend code in the same directory.

### Database
- [ ] Implement the schema via **Alembic migrations** — never use raw `CREATE TABLE` SQL or manual DB operations.
- [ ] Do **not** use mock data generators or hardcoded seed data in production code.
- [ ] Index the `readings` table on `(pool_id, created_at DESC)`.

### Backend
- [ ] Configure **CORS** on FastAPI to accept requests from `http://localhost:3000`.
- [ ] The `safety_engine.py` module must be a **pure function** with no database dependencies — pass the payload in, get status + alerts out.
- [ ] Validate that the `device_id` in every ingestion payload matches a registered pool in the `pools` table. Reject with `403` if not found.
- [ ] Alerts are **append-only** — never delete alert records. Only mark as `resolved = TRUE`.
- [ ] Implement `PATCH /api/v1/alerts/{alert_id}/resolve` endpoint.

### Frontend
- [ ] All components must be **fully responsive** using Tailwind utility classes.
- [ ] Per-parameter status badge colors in `MetricCard` must be calculated using the **Threshold Matrix** independently — not derived from global `safety_status`.
- [ ] The `HistoricalChart` must have **metric toggle buttons** to switch Y-axis between all 5 parameters.
- [ ] WebSocket connection must **gracefully reconnect** on drop (exponential backoff retry).
- [ ] The wearable PWA (`/watch` route) must trigger `navigator.vibrate()` only when status transitions **to** `unsafe` (not on every reading while unsafe).

### General
- [ ] All Python code must target Python 3.10+.
- [ ] All TypeScript code must be strictly typed — no `any` types.
- [ ] Do not expose raw database IDs in public API responses where UUIDs are available.
- [ ] Include a `requirements.txt` for the backend and `package.json` for the frontend.
- [ ] Include a `README.md` in each directory with setup and run instructions.

---

## Appendix A: API Reference Summary

| Method | Route | Description |
|---|---|---|
| `POST` | `/api/v1/ingest` | ESP32 → Backend: Submit sensor reading |
| `GET` | `/api/v1/pools` | Frontend → Backend: All pools + latest status |
| `GET` | `/api/v1/readings/{pool_id}?limit=40` | Frontend → Backend: Last N readings for chart |
| `GET` | `/api/v1/alerts/{pool_id}?resolved=false` | Frontend → Backend: Active alerts |
| `PATCH` | `/api/v1/alerts/{alert_id}/resolve` | Frontend → Backend: Mark alert as resolved |
| `WS` | `/ws/pool/{pool_id}` | Frontend ↔ Backend: Real-time bidirectional stream |

---

## Appendix B: Sample ESP32 JSON Payload

```json
{
  "device_id": "ESP32_01",
  "pool_id":   "pool_vit_01",
  "temperature": 28.5,
  "tds":         320.0,
  "turbidity":   12.4,
  "ph":          7.35,
  "orp":         695.0
}
```

---

## Appendix C: Environment Variables

### Backend (`backend/.env`)
```
DATABASE_URL=postgresql://user:password@localhost:5432/safedip
SECRET_KEY=your-secret-key
ENVIRONMENT=development
```

### Frontend (`frontend/.env.local`)
```
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_WS_BASE_URL=ws://localhost:8000
```

---

## 18. User Ecosystem & Allergy Logic (Technical Spec)

### 18.1 QR Deep-Linking
- QR Format: `https://<DOMAIN>/pool/<POOL_ID>`
- Dynamic Routing: Next.js handles this via `app/pool/[id]/page.tsx`.
- Auto-Connect: On load, the page extracts `id` from params and initializes WebSocket connection to `ws://<API>/ws/pool/<id>`.

### 18.2 Sensitivity Engine (Frontend-only)
- **Data Store**: LocalStorage (`safedip_user_prefs`).
- **Structure**: `{"skin_sensitive": bool, "eye_sensitive": bool, "respiratory_sensitive": bool}`.
- **Execution**:
  1. On `usePoolWebSocket` update, if `latestReading` exists:
  2. Check `prefs` from LocalStorage.
  3. If `readings.ph > 7.8 && prefs.skin_sensitive`, show Toast/Alert: "High pH may affect your sensitive skin."

---

*Document compiled from: SafeDip Project Documentation, SafeDip Business Requirements Document (BRD), and SafeDip System Context & Architecture Specification. Institution: Vellore Institute of Technology (VIT), Chennai.*
