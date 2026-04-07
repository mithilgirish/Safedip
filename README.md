<p align="center">
  <img src="docs/safedip%20logo.png" alt="SafeDip Logo" width="200"/>
</p>

# SafeDip: AI-Driven IoT Swimming Pool Safety Monitor

[![Next.js](https://img.shields.io/badge/Next.js-14-black)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110-009688)](https://fastapi.tiangolo.com/)
[![ESP32](https://img.shields.io/badge/ESP32-Arduino-E7352C)](https://www.espressif.com/)
[![PyTorch](https://img.shields.io/badge/PyTorch-LSTM-EE4C2C)](https://pytorch.org/)
[![License](https://img.shields.io/badge/License-MIT-blue)](LICENSE)

**SafeDip** is a commercial-grade, end-to-end IoT water safety platform. It continuously monitors water chemistry via an ESP32 sensor node and delivers real-time, **personalised safety analysis** to swimmers based on their individual skin biology — while providing pool operators with AI-powered predictive maintenance recommendations.

---

## 🌟 System Features

### 🔬 Real-Time Water Monitoring
- **5-parameter sensing**: pH, TDS (ppm), Turbidity (NTU), ORP (mV), Temperature (°C)
- **15-sample hardware averaging** per reading to eliminate sensor noise
- **Sub-10 second latency** from sensor to dashboard via WebSocket

### 🧠 AI / ML Layer
- **LSTM Neural Network**: Trained on synthetic time-series pool data to forecast water parameter drift 5 minutes ahead
- **Predictive Maintenance Engine**: Translates forecasts into operator-grade action recommendations (`full_replace`, `partial_replace`, `chemical`, `warning`, `nominal`)
- **Skin Safety AI**: Personalised rule-based engine that scores water safety (0–100) against dermatologically-informed thresholds specific to the user's skin type, conditions, and sensitivities

### 👤 Personalised Swimmer Safety
- Users select their **skin type** (Normal / Dry / Oily / Combination / Sensitive)
- Add **skin conditions** (Eczema, Psoriasis, Rosacea, Acne-prone)
- Toggle **Eye** and **Respiratory** sensitivities
- The dashboard card updates live with every reading showing a personal **SAFE / USE CAUTION / NOT SAFE FOR YOU** verdict

### 📡 Real-Time Infrastructure
- **WebSocket broadcasting**: Every ingested reading is pushed instantly to all connected dashboards
- **Auto pool registration**: New ESP32 devices are auto-registered on first POST — no manual setup
- **SQLite (dev) / PostgreSQL (prod)**: Seamless switch via `DATABASE_URL` environment variable

---

## 🏗️ System Architecture

```
┌─────────────────────┐        HTTP POST (JSON)       ┌──────────────────────────┐
│   ESP32 Edge Node   │ ─────────────────────────────▶ │   FastAPI Backend        │
│                     │                                │                          │
│  pH / TDS / Turb /  │                                │  ┌──────────────────┐   │
│  ORP / Temp sensors │                                │  │ Safety Engine    │   │
│  15-sample average  │                                │  │ (WHO thresholds) │   │
│  Temp compensation  │                                │  └──────────────────┘   │
└─────────────────────┘                                │  ┌──────────────────┐   │
                                                       │  │ LSTM Forecaster  │   │
         ┌─────────────────────────────────────────────│  │ + Decision Layer │   │
         │           WebSocket broadcast               │  └──────────────────┘   │
         ▼                                             │  ┌──────────────────┐   │
┌─────────────────────┐                               │  │ Skin Safety AI   │   │
│  Next.js Dashboard  │                               │  │ (POST /skin/     │   │
│                     │                               │  │  assess)         │   │
│  • Metrics Grid     │  POST /api/v1/skin/assess ──▶ │  └──────────────────┘   │
│  • Real-Time Chart  │ ◀── personalised score ──────  │                          │
│  • Skin Safety Card │                                │  SQLite / PostgreSQL     │
│  • ML Forecast Card │                                └──────────────────────────┘
│  • Alerts Feed      │
└─────────────────────┘
```

### The 4 Tiers
| Tier | Technology | Role |
|---|---|---|
| **1 — Edge** | ESP32 + Arduino C++ | Sensor reading, noise reduction, temperature compensation, HTTP POST |
| **2 — Backend** | FastAPI (Python) | Ingestion, safety evaluation, LSTM inference, WebSocket broadcast, Skin AI |
| **3 — Database** | SQLite (dev) / PostgreSQL (prod) via SQLAlchemy | Telemetry storage, alert log, pool registry |
| **4 — Frontend** | Next.js 14, Tailwind CSS, Recharts | Live dashboard, skin profile wizard, ML forecast display |

---

## 🧬 Skin Safety AI

The Skin AI module (`backend/app/ml/skin_ai.py`) is a dermatologically-informed rule engine — no training required.

| Skin Type | pH Safe Range | Notes |
|---|---|---|
| Normal | 7.0 – 7.8 | Baseline WHO-aligned range |
| Dry | 7.2 – 7.5 | Tighter — high pH strips skin lipids |
| Oily | 6.8 – 7.6 | Slightly wider tolerance |
| Combination | 7.0 – 7.6 | Moderate range |
| Sensitive | 7.2 – 7.5 | Most restrictive |

Conditions (Eczema, Psoriasis, Rosacea, Acne) apply further overrides. Eye and Respiratory sensitivities adjust ORP (chlorine) and TDS (chloramine) thresholds.

**API**: `POST /api/v1/skin/assess` — stateless, works for both fixed pool readings and portable water scans.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+, Node.js 18+, Arduino IDE (for hardware)

### 1. Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux/Mac
pip install -r requirements.txt
uvicorn app.main:app --reload
# API live at http://localhost:8000
# Swagger docs at http://localhost:8000/docs
```

### 2. Frontend
```bash
cd frontend
npm install
npm run dev
# Dashboard at http://localhost:3000
```

### 3. Simulator (no hardware needed)
```bash
# From project root, with backend running:
python simulate_hardware.py
# Sends realistic drifting sensor data every 3 seconds
```

### 4. Real Hardware (ESP32)
- Open `hardware/safedip_v0.5/safedip_v0.5.ino` in Arduino IDE
- Update `WIFI_SSID`, `WIFI_PASSWORD`, and `SERVER_URL` to your PC's local IP
- Flash to ESP32, dip sensors in water

---

## 📂 Project Structure

```
safedip/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point + CORS + router registration
│   │   ├── models.py            # SQLAlchemy ORM (Pool, Reading, Alert)
│   │   ├── schemas.py           # Pydantic request/response models
│   │   ├── safety_engine.py     # WHO-aligned threshold evaluation
│   │   ├── database.py          # DB engine + session factory
│   │   ├── websocket.py         # WebSocket connection manager
│   │   ├── ml/
│   │   │   ├── skin_ai.py       # 🆕 Skin Safety AI — personalised scoring engine
│   │   │   ├── predict.py       # LSTM inference pipeline
│   │   │   ├── decision.py      # Maintenance action decision layer
│   │   │   ├── model.py         # SafeDipLSTM architecture
│   │   │   ├── train.py         # Training script
│   │   │   ├── dataset.py       # Data loading + sliding windows
│   │   │   ├── generate_data.py # Synthetic training data generator
│   │   │   └── artifacts/       # Trained model weights + scaler
│   │   └── routers/
│   │       ├── ingest.py        # POST /api/v1/ingest
│   │       ├── pools.py         # Pool CRUD
│   │       ├── readings.py      # Historical readings
│   │       ├── alerts.py        # Alert feed
│   │       ├── recommend.py     # ML maintenance recommendations
│   │       └── skin.py          # 🆕 POST /api/v1/skin/assess
│   ├── data/                    # Training CSV data
│   └── requirements.txt
│
├── frontend/
│   ├── app/
│   │   ├── page.tsx             # Main dashboard
│   │   └── preferences/
│   │       └── page.tsx         # 🆕 3-step skin profile wizard
│   ├── components/
│   │   ├── SafetyBanner.tsx     # Global status banner
│   │   ├── MetricsGrid.tsx      # Live parameter cards
│   │   ├── HistoricalChart.tsx  # Recharts time-series graph
│   │   ├── MLForecastCard.tsx   # LSTM recommendation display
│   │   ├── AlertsFeed.tsx       # Live alert log
│   │   └── SkinSafetyCard.tsx   # 🆕 Personalised skin safety score card
│   └── hooks/
│       └── usePoolWebSocket.ts  # Real-time data hook
│
├── hardware/
│   └── safedip_v0.5/
│       └── safedip_v0.5.ino    # ESP32 firmware (pH, TDS, Turbidity, Temp)
│
├── ml/                          # Standalone ML documentation
│   └── README.md
│
├── simulate_hardware.py         # Software ESP32 simulator for development
└── README.md
```

---

## 🔌 API Reference

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/ingest` | Receive sensor reading from ESP32, evaluate safety, broadcast |
| `GET` | `/api/v1/readings/{pool_id}` | Fetch historical readings |
| `GET` | `/api/v1/alerts/{pool_id}` | Fetch alert history |
| `GET` | `/api/v1/pools` | List registered pools |
| `POST` | `/api/v1/recommend/{pool_id}` | Get LSTM-powered maintenance recommendation |
| `POST` | `/api/v1/skin/assess` | **🆕** Get personalised skin safety score for any water reading |
| `WS` | `/ws/pool/{pool_id}` | Subscribe to real-time pool data stream |

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python, FastAPI, SQLAlchemy, Pydantic, WebSockets |
| **ML / AI** | PyTorch (LSTM), scikit-learn (scaler), NumPy, pandas |
| **Frontend** | TypeScript, Next.js 14, Tailwind CSS, Recharts, Lucide |
| **Hardware** | C++ / Arduino, ArduinoJson, DallasTemperature, OneWire |
| **Database** | SQLite (development), PostgreSQL (production) |

---

© 2026 SafeDip — Vellore Institute of Technology (VIT), Chennai. Built for commercial pool safety and modern facility management.
