# AirVision India

**ISRO Problem Statement 3:** Development of Surface AQI & Identification of HCHO Hotspots over India using Satellite Data.

AirVision India is a production-ready full-stack platform that integrates CPCB ground air quality data, Sentinel-5P satellite pollutants (NO₂, SO₂, CO, O₃, HCHO), ERA5 weather data, and NASA FIRMS fire detections to monitor, predict, and explain air quality across India.

---

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Next.js 15     │────▶│  FastAPI Backend │────▶│  PostgreSQL     │
│  Frontend       │     │  REST API        │     │  Database       │
└─────────────────┘     └────────┬─────────┘     └─────────────────┘
                                 │
                    ┌────────────┼────────────┐
                    ▼            ▼            ▼
              ┌─────────┐  ┌─────────┐  ┌──────────┐
              │  Redis  │  │ Celery  │  │ XGBoost  │
              │  Cache  │  │ Workers │  │ + SHAP   │
              └─────────┘  └─────────┘  └──────────┘
```

## Tech Stack

| Layer | Technologies |
|-------|-------------|
| Frontend | Next.js 15, TypeScript, Tailwind CSS, Shadcn UI, Leaflet.js, Recharts |
| Backend | FastAPI, SQLAlchemy, PostgreSQL, Redis, Celery |
| ML/AI | XGBoost (PM2.5), DBSCAN (HCHO hotspots), SHAP (explainability), CNN-LSTM (future) |
| Data | CPCB, Sentinel-5P, ERA5, NASA FIRMS |

## Features

1. **Dashboard** — Current AQI map, category distribution, 30-day trend charts
2. **AQI Prediction** — XGBoost PM2.5 prediction, CPCB AQI calculation, heatmaps
3. **HCHO Hotspots** — DBSCAN cluster detection, temporal analysis
4. **Fire Correlation** — NASA FIRMS overlay, HCHO-fire correlation
5. **Transport Analysis** — ERA5 wind vectors, pollution transport paths
6. **Explainable AI** — SHAP feature importance, pollutant contribution charts
7. **Admin Panel** — Dataset management, model retraining, task monitoring

---

## Quick Start (Docker)

```bash
# Clone and configure
cp .env.example .env

# Start all services
docker compose up --build

# Access
# Frontend:  http://localhost:3000
# API Docs:  http://localhost:8000/docs
# Health:    http://localhost:8000/health
```

**Default credentials:**
- Admin: `admin@airvision.in` / `admin123`
- Analyst: `analyst@airvision.in` / `analyst123`

---

## Local Development

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Start PostgreSQL & Redis (or use Docker for just infra)
docker compose up postgres redis -d

uvicorn app.main:app --reload --port 8000
```

### Celery Worker

```bash
cd backend
celery -A app.tasks.celery_app worker --loglevel=info
celery -A app.tasks.celery_app beat --loglevel=info
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

---

## Project Structure

```
airvision-india/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # REST API routes
│   │   ├── core/            # Auth & security
│   │   ├── models/          # SQLAlchemy models
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── services/
│   │   │   ├── ml/          # XGBoost, DBSCAN, SHAP, transport
│   │   │   └── seed_data.py # Demo data seeder
│   │   ├── tasks/           # Celery async tasks
│   │   ├── utils/           # AQI calculation (CPCB)
│   │   ├── config.py
│   │   ├── database.py
│   │   └── main.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── app/             # Next.js App Router pages
│   │   ├── components/      # UI, maps, charts, layout
│   │   └── lib/             # API client, utilities
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | System health check |
| POST | `/api/v1/auth/login` | JWT authentication |
| GET | `/api/v1/dashboard/summary` | Dashboard KPIs |
| GET | `/api/v1/dashboard/trends` | AQI trend data |
| GET | `/api/v1/dashboard/map` | Current AQI map points |
| POST | `/api/v1/prediction/predict` | Predict AQI at location |
| GET | `/api/v1/prediction/heatmap` | AQI prediction heatmap |
| GET | `/api/v1/prediction/explain` | SHAP explanation |
| GET | `/api/v1/hotspots/` | List HCHO hotspots |
| POST | `/api/v1/hotspots/detect` | Run DBSCAN detection |
| GET | `/api/v1/fire/points` | NASA FIRMS fire points |
| GET | `/api/v1/fire/correlation` | Fire-HCHO correlation |
| GET | `/api/v1/transport/wind` | ERA5 wind vectors |
| GET | `/api/v1/transport/path` | Transport path simulation |
| GET | `/api/v1/admin/stats` | Admin system stats |
| POST | `/api/v1/admin/models/retrain` | Trigger model retraining |

Full interactive docs at `/docs` (Swagger UI).

---

## Database Schema

- **users** — Authentication & RBAC (admin, analyst, viewer)
- **air_quality_stations** — CPCB monitoring stations
- **air_quality_readings** — Ground PM2.5, PM10, gases, AQI
- **satellite_readings** — Sentinel-5P pollutant columns
- **weather_readings** — ERA5 temperature, humidity, wind
- **fire_points** — NASA FIRMS detections
- **aqi_predictions** — ML prediction history
- **hcho_hotspots** — DBSCAN cluster results
- **datasets** — Uploaded dataset registry
- **ml_models** — Model versioning & metrics
- **task_logs** — Celery task monitoring

---

## ML Pipeline

### AQI Prediction (XGBoost)
- **Input features:** NO₂, SO₂, CO, O₃, temperature, humidity, wind speed, lat/lon, hour, month
- **Output:** PM2.5 → CPCB National AQI
- **Explainability:** SHAP TreeExplainer

### HCHO Hotspot Detection (DBSCAN)
- Clusters Sentinel-5P HCHO readings spatially
- Classifies intensity: low / medium / high
- Temporal analysis over configurable date ranges

### Future: CNN-LSTM
- Placeholder at `backend/app/services/ml/cnn_lstm.py`
- Planned for spatiotemporal satellite tile sequences

---

## Deployment

### Production Checklist

1. Set strong `SECRET_KEY` in `.env`
2. Configure production PostgreSQL & Redis URLs
3. Set `CORS_ORIGINS` to your domain
4. Use `docker compose -f docker-compose.yml up -d` on your server
5. Put Nginx/Caddy in front for HTTPS
6. Set `NEXT_PUBLIC_API_URL` to your API domain

### Environment Variables

| Variable | Description |
|----------|-------------|
| `SECRET_KEY` | JWT signing key |
| `DATABASE_URL` | Async PostgreSQL connection |
| `DATABASE_URL_SYNC` | Sync PostgreSQL (Celery) |
| `REDIS_URL` | Redis cache |
| `CELERY_BROKER_URL` | Celery message broker |
| `CORS_ORIGINS` | Allowed frontend origins |
| `NEXT_PUBLIC_API_URL` | Backend URL for frontend |

---

## Data Sources

| Source | Variables | Usage |
|--------|-----------|-------|
| CPCB | PM2.5, PM10, NO₂, SO₂, CO, O₃ | Ground truth AQI |
| Sentinel-5P | NO₂, SO₂, CO, O₃, HCHO | Satellite columns |
| ERA5 | Temp, humidity, wind | Transport & ML features |
| NASA FIRMS | Fire radiative power | Biomass burning correlation |

---

## License

Built for ISRO Problem Statement 3 — Academic / Research use.
