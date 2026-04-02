# SafeDip: Project Progress Checkpoint & Build Guide

This document tracks the current state of the SafeDip IoT Swimming Pool Safety system and provides a step-by-step roadmap for finishing and building the application.

---

## 1. Project Status Checkpoint (as of April 2, 2026)

| Component | Status | Description |
|---|---|---|
| **Backend (FastAPI)** | ✅ **Functional** | Core API, Pydantic models, Safety threshold engine, and WebSocket broadcasting are implemented. |
| **Frontend (Next.js)** | ✅ **Initializing** | Framework set up, `npm install` completed, initial `usePoolWebSocket` hook and dashboard layout structure present. |
| **Hardware (ESP32)** | ✅ **Refined** | Firmware v0.6.0 refined with polynomial TDS, two-point pH calibration, real temperature sensing, and ORP support. |
| **Database** | ⚠️ **Schema Ready** | Alembic models defined; migrations need to be initialized and applied to a PostgreSQL/Supabase instance. |

---

## 2. Build & Setup Guide

### 📂 Phase 1: Backend Setup (Python)
1. **Navigate to backend**: `cd backend`
2. **Create Virtual Environment**: `python -m venv venv`
3. **Activate Environment**: `.\venv\Scripts\activate` (Windows)
4. **Install Dependencies**: `pip install -r requirements.txt`
5. **Database Configuration**:
   - Create a `.env` file in `backend/app/` with `DATABASE_URL=postgresql://user:pass@localhost/safedip`.
6. **Run Migrations**:
   - `alembic init alembic` (if not initialized)
   - `alembic revision --autogenerate -m "Initial schema"`
   - `alembic upgrade head`
7. **Start Server**: `uvicorn app.main:app --reload --host 0.0.0.0`

### 🌐 Phase 2: Frontend Setup (Next.js)
1. **Navigate to frontend**: `cd frontend`
2. **Install Packages**: `npm install`
3. **Configuration**: 
   - Ensure `next.config.js` or `tailwind.config.ts` are at the root.
   - Set the `API_BASE_URL` if different from `http://localhost:8000`.
4. **Start Dev Server**: `npm run dev` (Access at `http://localhost:3000`)

### ⚡ Phase 3: Hardware Deployment (ESP32)
1. **Open Arduino IDE**: Load `hardware/esp32_firmware/safedip_node.ino`.
2. **Install Libraries**:
   - `ArduinoJson`
   - `OneWire`
   - `DallasTemperature`
3. **Configure**: Update `WIFI_SSID`, `WIFI_PASS`, and your computer's IP in `API_ENDPOINT`.
4. **Flash**: Upload to your ESP32 board.

---

## 3. Pending Features / Backlog
- [ ] **Mobile User PWA**: Build the dynamic `/pool/[id]` route for public swimmers.
- [ ] **QR Deep-Linking**: Implementation of pool-specific data loading based on URL parameters.
- [ ] **Allergy/Sensitivity Engine**: LocalStorage logic to compare user preferences against real-time data.
- [ ] **Alembic Migration Initialization**: Formally generate the first migration from `models.py`.
- [ ] **PWA Manifest Setup**: Ensure the `public/manifest.json` is correctly configured for the wearable watch interface.
- [ ] **Dashboard Components**: Build out detailed UI for `MetricsGrid` and `HistoricalChart`.
- [ ] **User Auth**: Implement JWT-based authentication for administrative dashboard access.

---

### Verification Checklist
- [ ] Backend `/docs` (Swagger) is reachable.
- [ ] ESP32 Serial Monitor shows JSON payload transmission SUCCESS.
- [ ] Frontend receives real-time WebSocket updates from the backend.
- [ ] Database records high-velocity telemetry without loss.
