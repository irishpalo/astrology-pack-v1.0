# Astrology Compute API (FastAPI)

A minimal FastAPI service exposing two endpoints:

- `POST /natal-charts` — returns a generated `chartId` and placeholder `positions`.
- `POST /transits` — validates `targetDateTime` and returns a sample transit aspect.

## Local Run

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

Health check: `GET http://localhost:8000/` → `{ "status": "ok", "service": "Astrology Compute API" }`

## cURL Sanity Checks

Create chart:

```bash
curl -X POST http://localhost:8000/natal-charts \
  -H "Content-Type: application/json" \
  -d '{
    "date": "1992-05-17",
    "time": "20:30:00",
    "timezone": "Africa/Johannesburg",
    "latitude": -26.3833,
    "longitude": 27.3667,
    "house_system": "whole_sign",
    "zodiac": "tropical",
    "include": { "lots": true, "nodes": true, "sect": true, "visibility": true }
  }'
```

Compute transits:

```bash
curl -X POST http://localhost:8000/transits \
  -H "Content-Type: application/json" \
  -d '{
    "chartId": "chart_xxxxxxxx",
    "targetDateTime": "2025-09-04T12:00:00",
    "timezone": "Africa/Johannesburg",
    "orbDegrees": 3.0
  }'
```

## Render Deployment

Use the included `render.yaml` for a one‑click Blueprint deploy, or set up manually:

- **Build command**: `pip install -r requirements.txt`
- **Start command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
