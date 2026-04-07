# SafeDip Frontend (Next.js Dashboard)

The SafeDip frontend is a modern, real-time web application built with **Next.js 14 (App Router)**, **Tailwind CSS**, and **WebSockets**. It provides pool administrators with a comprehensive monitoring dashboard and swimmers with a personalised, skin-type-aware water safety companion.

---

## 📱 Pages & Routes

### `/` — Main Dashboard
The real-time control centre. Connects to the backend WebSocket and renders live data instantly:
- **Safety Banner**: Full-width SAFE / CAUTION / UNSAFE status bar with colour-coded glow
- **Metrics Grid**: Five parameter cards (Temp, pH, TDS, Turbidity, ORP) each with individual status badges
- **Real-Time Telemetry Chart**: Recharts line graph with parameter toggles; auto-scrolls with each new reading
- **Skin Safety Card** *(new)*: Personalised 0–100 score ring, status badge, advice, and expandable per-parameter breakdown — automatically calls `POST /api/v1/skin/assess` on every new reading
- **ML Forecast Card**: LSTM-powered maintenance recommendation (action, urgency, 5-minute parameter forecast)
- **Alerts Feed**: Live log of all threshold breach events

### `/preferences` — Skin Profile Wizard *(new)*
A 3-step guided setup that saves the user's skin profile to `localStorage` (`safedip_skin_profile`):

| Step | What it captures |
|---|---|
| 1 — Skin Type | Normal / Dry / Oily / Combination / Sensitive |
| 2 — Conditions | Eczema / Psoriasis / Rosacea / Acne-prone / None (multi-select) |
| 3 — Sensitivities | Eye sensitivity (chlorine), Respiratory sensitivity (asthma/chloramines) |

Profile data stays on-device — nothing is ever sent to a server. The Skin Safety Card reads it and sends it (paired with the latest reading) to the backend for assessment.

---

## 🛠️ Setup & Running

### Prerequisites
- Node.js 18+

### Installation
```bash
cd frontend
npm install
```

### Development Server
```bash
npm run dev
# Open http://localhost:3000
```

### Environment Variables
Create `.env.local` if the backend runs on a non-default address:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```
If this variable is absent, the frontend defaults to `http://localhost:8000`.

---

## 🏗️ Internal Structure

```
frontend/
├── app/
│   ├── layout.tsx               # Root layout — fonts, global styles
│   ├── globals.css              # Tailwind base + custom CSS tokens
│   ├── page.tsx                 # Main dashboard (/) — composes all components
│   └── preferences/
│       └── page.tsx             # 3-step skin profile wizard (/preferences)
│
├── components/
│   ├── SafetyBanner.tsx         # Global pool status banner (safe/caution/unsafe)
│   ├── MetricsGrid.tsx          # 5-parameter live metric cards
│   ├── HistoricalChart.tsx      # Recharts real-time line chart with tab toggles
│   ├── MLForecastCard.tsx       # LSTM recommendation display card
│   ├── AlertsFeed.tsx           # Scrollable live alert log
│   └── SkinSafetyCard.tsx       # Personalised skin safety score + breakdown
│
└── hooks/
    └── usePoolWebSocket.ts      # WebSocket hook — emits latestReading, latestAlerts, recommendation
```

### Key Data Flow
```
usePoolWebSocket(poolId)
    ↓  WebSocket message
latestReading, latestAlerts, recommendation
    ↓
page.tsx distributes props to:
    ├── SafetyBanner       ← latestReading.safety_status
    ├── MetricsGrid        ← latestReading (all parameters)
    ├── HistoricalChart    ← latestReading (triggers re-fetch of history)
    ├── SkinSafetyCard     ← latestReading → POST /api/v1/skin/assess → renders result
    ├── MLForecastCard     ← recommendation
    └── AlertsFeed         ← latestAlerts
```

---

## 🧬 Skin Safety Card — How It Works

1. On mount, reads `safedip_skin_profile` from `localStorage`
2. If no profile → renders a "Set Up Profile" CTA pointing to `/preferences`
3. If backend offline → shows error message (never crashes the dashboard)
4. On each new `latestReading`: POSTs `{ reading, skin_profile }` to `POST /api/v1/skin/assess`
5. Renders:
   - **Animated SVG score ring** (0–100, colour matches status)
   - **Status badge**: SAFE FOR YOU / USE CAUTION / NOT SAFE FOR YOU
   - **Advice text** and skin type tags
   - **Parameter breakdown**: each of pH, TDS, Turbidity, Temp, ORP as a tappable row that expands to show detailed advice

---

## 🎨 Design System

- **Color palette**: Deep navy `#030712` base, Zinc 900 cards, Indigo 500 accent
- **Typography**: Outfit font (Google Fonts) for headings, system sans for body
- **Animation**: `tailwindcss-animate` — fade-in, slide-in-from-top/bottom on initial load
- **Effects**: Glassmorphism (`backdrop-blur-xl`), gradient glows on status-coloured cards
- **Icons**: Lucide React
