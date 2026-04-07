# SafeDip Backend (FastAPI)

The SafeDip backend is a high-performance Python API responsible for **data ingestion**, **safety evaluation**, **LSTM-powered predictive maintenance**, **personalised skin safety analysis**, and **real-time WebSocket broadcasting** of water quality telemetry.

---

## 🚀 Key Features

- **FastAPI Core**: Async-capable, fully typed API with auto-generated Swagger docs at `/docs`
- **Safety Engine**: Rule-based threshold classifier (WHO-aligned) → `safe` / `caution` / `unsafe`
- **LSTM Forecaster**: Pre-trained PyTorch model predicts the next 5 minutes of water parameter drift
- **Predictive Maintenance**: Decision layer translates LSTM output into operator actions (`full_replace`, `chemical`, `warning`, etc.)
- **Skin Safety AI** *(new)*: Stateless endpoint scores any water reading against per-skin-type dermatological thresholds — no ML model training required
- **WebSocket Manager**: Pushes every ingested reading + alerts + ML recommendation to all connected dashboard clients in real time
- **Auto Pool Registration**: First reading from an unknown `device_id` automatically creates a pool record — zero configuration needed for new hardware
- **SQLite / PostgreSQL**: Dev uses SQLite (`safedip.db`) out of the box; set `DATABASE_URL` for PostgreSQL in production

---

## 🛠️ Setup & Running

### 1. Prerequisites
- Python 3.10+

### 2. Installation
```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac
pip install -r requirements.txt
```

### 3. Environment Config
By default the backend uses SQLite locally. For PostgreSQL, create `.env`:
```
DATABASE_URL=postgresql://user:password@localhost/safedip
```

### 4. Running
```bash
uvicorn app.main:app --reload
```
- **API**: `http://localhost:8000`
- **Swagger docs**: `http://localhost:8000/docs`

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/ingest` | Receive ESP32 sensor payload, evaluate + broadcast |
| `GET` | `/api/v1/readings/{pool_id}` | Historical readings (supports `?limit=N`) |
| `GET` | `/api/v1/alerts/{pool_id}` | Alert event history |
| `GET` | `/api/v1/pools` | List all registered pools |
| `POST` | `/api/v1/recommend/{pool_id}` | LSTM predictive maintenance recommendation |
| `POST` | `/api/v1/skin/assess` | Personalised skin safety score for any water reading |
| `WS` | `/ws/pool/{pool_id}` | Real-time data stream (reading + alerts + recommendation) |

### Skin Assess — Request Shape
```json
POST /api/v1/skin/assess
{
  "reading": {
    "ph": 7.4,
    "tds": 520.0,
    "turbidity": 18.5,
    "temperature": 28.2,
    "orp": 695.0        // optional — omit if sensor absent
  },
  "skin_profile": {
    "skin_type": "dry",               // normal | dry | oily | combination | sensitive
    "conditions": ["eczema"],         // eczema | psoriasis | rosacea | acne | none
    "eye_sensitive": false,
    "respiratory_sensitive": false
  }
}
```

---

## 🏗️ Internal Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI app, CORS, router registration
│   ├── models.py            # SQLAlchemy ORM — Pool, Reading, Alert
│   ├── schemas.py           # Pydantic request/response models
│   ├── safety_engine.py     # Pure function: reading → safe/caution/unsafe + alert messages
│   ├── database.py          # Engine + SessionLocal + Base
│   ├── websocket.py         # Connection manager + broadcast_to_pool()
│   ├── ml/
│   │   ├── skin_ai.py       # Personalised skin safety engine (stateless rule engine)
│   │   ├── predict.py       # LSTM inference: readings → forecast array → recommendation
│   │   ├── decision.py      # Forecast → maintenance action decision
│   │   ├── model.py         # SafeDipLSTM (PyTorch seq2seq architecture)
│   │   ├── train.py         # Training loop
│   │   ├── dataset.py       # CSV → sliding windows → DataLoader
│   │   ├── generate_data.py # Synthetic pool data generation
│   │   └── artifacts/       # safedip_lstm.pt + scaler.pkl (pre-trained)
│   └── routers/
│       ├── ingest.py        # Ingestion pipeline (safety → DB → ML → WebSocket)
│       ├── pools.py         # Pool CRUD
│       ├── readings.py      # Reading history
│       ├── alerts.py        # Alert history
│       ├── recommend.py     # On-demand LSTM recommendation
│       └── skin.py          # Skin safety assessment endpoint
└── requirements.txt
```

---

## 🧬 Skin Safety AI

`app/ml/skin_ai.py` is a pure Python rule engine — no model file needed. It:
1. Looks up per-skin-type pH tolerance windows (5 types × 4 thresholds)
2. Applies condition overrides (Eczema, Psoriasis, Rosacea, Acne tighten the range further)
3. Adjusts ORP (chlorine) limits for eye sensitivity
4. Adjusts TDS (chloramine proxy) limits for respiratory sensitivity
5. Weights all parameters → returns a 0–100 score, overall status, full parameter breakdown, and human-readable advice

---

## 🤖 ML Pipeline

The LSTM forecaster (`ml/predict.py`) runs automatically on every `/ingest` call once 30+ readings exist:

```
Last 30 readings (chronological)
        ↓
  MinMaxScaler (saved scaler.pkl)
        ↓
  SafeDipLSTM  (1, 30, 5) → (1, 10, 5)
        ↓
  Inverse transform → real units
        ↓
  decision.decide() → action recommendation
        ↓
  WebSocket broadcast → dashboard
```

If the model files are missing, the system falls back to a simple linear extrapolation so ingestion never breaks.
