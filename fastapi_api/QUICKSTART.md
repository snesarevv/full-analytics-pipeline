# Quick Start Guide

## Start the Stack

```bash
cd fastapi_api
cp .env.example .env
docker compose up --build
```

Wait 30 seconds for health checks, then verify everything works.

## Verify Everything Works

### 1. API up?
```bash
curl -s http://localhost:8000/healthz
```
**Expect**: `{"status":"ok"}`

### 2. DB reachable via API?
```bash
curl -s http://localhost:8000/api/v1/meta/counts
```
**Expect**: `{"app_profile": <int>, "appointment": <int>, "ab_event": <int>}`

### 3. Metrics exposed?
```bash
curl -s http://localhost:8000/metrics | head
```
**Expect**: Prometheus text (e.g., `HELP`/`TYPE` lines, `http_request_duration_*`)

### 4. Structured logs with request ID?
```bash
docker compose logs api | tail -5
curl -H "X-Request-Id: demo-123" -s http://localhost:8000/healthz > /dev/null
docker compose logs api | tail -1
```
**Expect**: JSON log line including `request_id=demo-123`, `method`, `path`, `status_code`, `duration_ms`

### 5. Rate limit works?
```bash
for i in {1..35}; do curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8000/healthz; done
```
**Expect**: First ~28 show `200`, final few show `429`

### 6. Tests pass?
```bash
docker compose exec api bash -c "cd /app && PYTHONPATH=/app pytest -q"
```
**Expect**: All green

### 7. Data quality (dbt tests)?
```bash
docker compose exec api bash -c "cd /app/dbt && dbt build && dbt test"
```
**Expect**: Models build, tests pass (`not_null`, `accepted_values`, etc.)

## Quick API Examples

```bash
# A/B test events (Test group only)
curl "http://localhost:8000/api/v1/ab_events?group=Test&limit=10"

# Appointments (Attended status)
curl "http://localhost:8000/api/v1/appointments?appointment_status=Attended&limit=10"

# App profiles (Google Ads traffic)
curl "http://localhost:8000/api/v1/app_profiles?traffic_source=Google%20Ads&limit=10"

# Date range query
curl "http://localhost:8000/api/v1/appointments?date_from=2023-07-01&date_to=2023-07-31"
```

## Development

### Restart after code changes
```bash
docker compose restart api
```

### Add new dbt model
```bash
# 1. Create SQL file in dbt/models/
# 2. Build and test
docker compose exec api bash -c "cd /app/dbt && dbt run --select your_model && dbt test --select your_model"
```

### Access database directly
```bash
docker exec -it fastapi_api-db-1 psql -U app -d appdb
```

## Troubleshooting

```bash
# Check logs
docker compose logs api
docker compose logs db

# Restart everything
docker compose down
docker compose up -d

# Clean slate (deletes data)
docker compose down -v
```

## Next Steps

- **API docs**: http://localhost:8000/docs
- **Metrics**: http://localhost:8000/metrics
- **Production guide**: [PRODUCTION_GUIDE.md](PRODUCTION_GUIDE.md)
