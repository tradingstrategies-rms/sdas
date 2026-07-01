# SDAS — Singapore Dividend Accumulation Screener

> Automatically screens 14 SGX dividend stocks daily. Sends a BUY / WATCHLIST / OVERVALUED email at 7:30 PM SGT every weekday. Goal: SGD 5,000/month passive income.

---

## Architecture

```
frontend/          Next.js 15 + Tailwind + Recharts  →  Vercel
backend/           FastAPI + yfinance                 →  Google Cloud Run
Firestore          stocks · daily_prices · signals · portfolio
Cloud Scheduler    triggers /api/v1/scheduler/trigger at 7:15 PM SGT
SendGrid           daily signal email digest
```

---

## Quick Start (Local)

### 1. Clone

```bash
git clone https://github.com/you/sdas.git
cd sdas
```

### 2. Backend setup

```bash
cd backend
cp .env.example .env
# Fill in Firebase + SendGrid credentials in .env
pip install -r requirements.txt
```

### 3. Seed Firestore

```bash
cd backend
python seed.py
```

### 4. Run backend

```bash
uvicorn app.main:app --reload --port 8080
```

API docs: http://localhost:8080/docs

### 5. Frontend setup

```bash
cd frontend
cp .env.local.example .env.local
# Fill in Firebase web SDK credentials
npm install
npm run dev
```

App: http://localhost:3000

### Or use Docker Compose

```bash
docker-compose up --build
```

---

## Scoring System (max 19 points)

| Component | Details | Max |
|-----------|---------|-----|
| Trend | Price vs SMA50/SMA200 | 4 |
| Pullback | Drawdown from 52w high | 3 |
| Dividend | Category-specific yield thresholds | 3 |
| Valuation | PB vs 5-year average | 2 |
| RSI | Oversold signal | 3 |
| Market Correction | STI drawdown bonus | 4 |

**Signals:**
- 🟢 **BUY NOW** — score ≥ 13, yield ≥ 4%, price > SMA200 → SGD 750
- 🟡 **WATCHLIST** — score 9–12, yield ≥ 4%, price > SMA200 → SGD 500
- 🔴 **OVERVALUED** — anything else → SGD 0

---

## Deployment

### Backend → Google Cloud Run

```bash
cd backend

# Build and push
gcloud builds submit --tag gcr.io/YOUR_PROJECT/sdas-backend

# Deploy
gcloud run deploy sdas-backend \
  --image gcr.io/YOUR_PROJECT/sdas-backend \
  --platform managed \
  --region asia-southeast1 \
  --allow-unauthenticated \
  --set-env-vars FIREBASE_PROJECT_ID=xxx,SENDGRID_API_KEY=xxx,...
```

### Schedule → Google Cloud Scheduler

```bash
# Weekdays 7:15 PM SGT = 11:15 UTC
gcloud scheduler jobs create http sdas-screener-run \
  --location=asia-southeast1 \
  --schedule="15 11 * * 1-5" \
  --uri="https://YOUR_CLOUD_RUN_URL/api/v1/scheduler/trigger" \
  --headers="Content-Type=application/json,X-Scheduler-Secret=YOUR_SECRET" \
  --message-body='{}' \
  --time-zone="UTC"
```

See `docs/cloud_scheduler_setup.sh` for the full script.

### Frontend → Vercel

```bash
cd frontend
npx vercel --prod
# Set env vars in Vercel dashboard: NEXT_PUBLIC_API_URL, Firebase keys
```

---

## Tests

```bash
cd backend
pip install pytest
pytest tests/ -v
```

---

## Environment Variables

### Backend (`backend/.env`)

| Variable | Description |
|----------|-------------|
| `FIREBASE_PROJECT_ID` | Firebase project ID |
| `FIREBASE_PRIVATE_KEY` | Service account private key |
| `FIREBASE_CLIENT_EMAIL` | Service account email |
| `SENDGRID_API_KEY` | SendGrid API key |
| `EMAIL_FROM` | Sender email |
| `EMAIL_TO` | Recipient email |
| `SCHEDULER_SECRET` | Shared secret for Cloud Scheduler |
| `MIN_DIVIDEND_YIELD` | Min yield threshold (default: 4.0) |
| `BUY_NOW_AMOUNT` | SGD amount for BUY NOW (default: 750) |

### Frontend (`frontend/.env.local`)

| Variable | Description |
|----------|-------------|
| `NEXT_PUBLIC_API_URL` | Backend URL |
| `NEXT_PUBLIC_FIREBASE_API_KEY` | Firebase web API key |
| `NEXT_PUBLIC_FIREBASE_PROJECT_ID` | Firebase project ID |

---

## Firestore Collections

| Collection | Purpose |
|-----------|---------|
| `stocks` | Watchlist metadata (category, target yield) |
| `daily_prices` | OHLCV + technicals per date per ticker |
| `signals` | BUY/WATCH/OVER signals per date per ticker |
| `portfolio` | Aggregated portfolio value snapshot |

---

## Watchlist

14 SGX dividend stocks across Banks, REITs, Infrastructure, and Equities:

DBS · UOB · SingTel · SATS · Jardine C&C · CapitaLand Investment · Ascendas REIT · CapitaLand Integrated Commercial Trust · Keppel Infrastructure Trust · Frasers Centrepoint Trust · Mapletree Industrial Trust · Mapletree Pan Asia Commercial Trust · Frasers Logistics & Commercial Trust · Keppel DC REIT

---

## Roadmap

- [x] Scoring engine
- [x] Daily screener + email
- [x] FastAPI backend
- [x] Next.js dashboard
- [x] Backtest engine
- [ ] Firebase Auth login
- [ ] Dividend calendar (ex-date tracking)
- [ ] Transaction ledger + cost basis
- [ ] Performance vs STI chart
- [ ] Mobile push notifications (FCM)
- [ ] CSV export
