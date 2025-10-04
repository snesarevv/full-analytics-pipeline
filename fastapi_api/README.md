# Analytics API

FastAPI application that loads three CSVs into Postgres and exposes clean, versioned REST endpoints for analytics extraction.

## What This Service Does

**Data ingestion**: Reads CSV files on startup and seeds Postgres tables (idempotent—safe to restart).

**Data transformation**: dbt models transform raw data through staging views into analytics-ready marts.

**API layer**: Versioned REST endpoints (`/api/v1/`) with pagination, filtering, and stable contracts for downstream consumers.

**Observability**: Structured JSON logs, Prometheus metrics, and health checks for monitoring and orchestration.

**Safety**: Rate limiting and graceful degradation prevent cascading failures under load.

## Data Flow: Sources → Staging → Marts

### Sources (Raw Tables)
Seeded from CSVs on startup (idempotent):

- **`app_profile`**: `patient_id`, `traffic_source`, `device`
- **`appointment`**: `patient_id`, `age`, `gender`, `doctor_name`, `appointment_reason`, `appointment_date`, `appointment_status`
- **`ab_event`**: `patient_id`, `group`, `event_name`, `event_datetime`

### Staging (dbt Views)
Clean, typed views that normalize enums and standardize column names:

- **`stg_app_profile`**: Cast types, normalize traffic sources
- **`stg_appointment`**: Standardize appointment statuses, cast dates
- **`stg_ab_event`**: Clean group names, cast timestamps

### Marts (dbt Tables)
Analytics-ready tables used by BI tools and downstream jobs:

- **`dim_patient_from_app_profiles`**: Patient dimension with acquisition data
- **`fct_appointments`**: Appointment facts with status and timing
- **`fct_ab_events`**: A/B test event facts for experiment analysis

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Your CSV files in `/mnt/data/` directory

### Setup & Run

1. **Copy environment file:**
   ```bash
   cd fastapi_api
   cp .env.example .env
   ```

2. **Start the application:**
   ```bash
   docker-compose up --build
   ```

3. **Access the API:**
   - API Documentation: http://localhost:8000/docs
   - Alternative Docs: http://localhost:8000/redoc
   - Health Check: http://localhost:8000/healthz

## 📡 API Endpoints

### Health & Metadata

- **`GET /healthz`** - Application health check
- **`GET /api/v1/meta/health`** - Database health check
- **`GET /api/v1/meta/counts`** - Record counts for all tables

### A/B Test Events

- **`GET /api/v1/ab_events/`** - List A/B test events
  - Query params: `limit`, `offset`, `patient_id`, `group`, `event_name`, `since`, `before`
- **`GET /api/v1/ab_events/page`** - Get pagination info

### Appointments

- **`GET /api/v1/appointments/`** - List appointments
  - Query params: `limit`, `offset`, `patient_id`, `appointment_status`, `doctor_name`, `appointment_reason`, `date_from`, `date_to`

### App Profiles

- **`GET /api/v1/app_profiles/`** - List app profiles
  - Query params: `limit`, `offset`, `traffic_source`, `device_like`

## 🔍 Example API Calls

```bash
# Check health
curl localhost:8000/healthz
curl localhost:8000/api/v1/meta/health

# Get record counts
curl localhost:8000/api/v1/meta/counts

# Filter A/B events by group and event name
curl "localhost:8000/api/v1/ab_events?group=Test&event_name=appointment_confirmed&limit=5"

# Filter appointments by status
curl "localhost:8000/api/v1/appointments?appointment_status=Attended&limit=5"

# Filter profiles by traffic source
curl "localhost:8000/api/v1/app_profiles?traffic_source=Apple%20Ads&limit=5"

# Date range query for appointments
curl "localhost:8000/api/v1/appointments?date_from=2023-07-01&date_to=2023-07-31"
```

## Project Structure

```
fastapi_api/
├── app/
│   ├── core/
│   │   ├── config.py          # Settings & configuration
│   │   ├── database.py        # SQLAlchemy setup
│   │   └── logging.py         # Structured logging & request IDs
│   ├── models/
│   │   ├── app_profile.py     # AppProfile model
│   │   ├── appointment.py     # Appointment model
│   │   └── ab_event.py        # ABEvent model
│   ├── schemas/
│   │   ├── common.py          # Shared schemas
│   │   ├── app_profile.py     # AppProfile schemas
│   │   ├── appointment.py     # Appointment schemas
│   │   └── ab_event.py        # ABEvent schemas
│   ├── services/
│   │   ├── seed.py            # CSV seeding logic
│   │   └── stats.py           # Analytics functions
│   ├── api/
│   │   └── v1/
│   │       ├── router.py      # Main router
│   │       ├── app_profiles.py
│   │       ├── appointments.py
│   │       ├── ab_events.py
│   │       └── meta.py
│   └── main.py                # FastAPI app entrypoint
├── dbt/                       # dbt transformations
│   ├── dbt_project.yml
│   ├── profiles.yml
│   └── models/
│       ├── sources.yml
│       ├── schema.yml         # dbt tests (data quality)
│       ├── staging/           # Cleaned views
│       └── marts/             # Business tables
├── tests/                     # pytest suite
│   ├── conftest.py
│   ├── test_meta.py
│   └── test_contracts.py
├── data/                      # CSV files
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── .env.example
```

## ⚙️ Configuration

Edit `.env` file to customize:

```env
DB_URL=postgresql+psycopg://app:app@db:5432/appdb
AUTO_SEED=true
DATA_DIR=/mnt/data
LOG_LEVEL=INFO
```

## 🗄️ Database Schema

### `app_profile` table
- `patient_id` (PK, indexed)
- `traffic_source` (indexed)
- `device` (indexed)

### `appointment` table
- `id` (PK, auto-increment)
- `patient_id` (indexed)
- `age`
- `gender` (indexed)
- `doctor_name` (indexed)
- `appointment_reason` (indexed)
- `appointment_date` (indexed)
- `appointment_status` (indexed)
- Composite index: `(patient_id, appointment_date, appointment_reason)`

### `ab_event` table
- `id` (PK, auto-increment)
- `patient_id` (indexed)
- `group` (indexed)
- `event_name` (indexed)
- `event_datetime` (indexed)
- Unique constraint: `(patient_id, event_name, event_datetime)`

## 🔄 Data Seeding

The application automatically seeds data on startup if `AUTO_SEED=true`:

- **Idempotent**: Re-running won't create duplicates
- **App Profiles**: Upserts by `patient_id`
- **Appointments**: Skips existing `(patient_id, appointment_date, appointment_reason)` combinations
- **A/B Events**: Skips existing `(patient_id, event_name, event_datetime)` combinations

## 🛠️ Development

### Run locally without Docker:

```bash
# Install dependencies
pip install -r requirements.txt

# Set up PostgreSQL (adjust .env accordingly)
# Then run:
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Access PostgreSQL directly:

```bash
docker exec -it fastapi_api-db-1 psql -U app -d appdb
```

## Observability

### Structured Logs
JSON logs with `request_id`, `method`, `path`, `status_code`, and `duration_ms`—ready to ship to ELK or Grafana Loki:

```json
{
  "timestamp": "2025-10-04T12:58:47Z",
  "level": "info",
  "message": "http_request",
  "request_id": "abc-123",
  "method": "GET",
  "path": "/api/v1/appointments",
  "status_code": 200,
  "duration_ms": 45
}
```

### Prometheus Metrics
`/metrics` endpoint exposes:
- Request rate and latency histograms
- In-flight request gauge
- Status code distribution

Plug into Grafana for SLIs/SLOs.

### Health Checks
- **`/healthz`**: Application readiness
- **`/api/v1/meta/health`**: Database liveness

Use these for Kubernetes readiness/liveness probes or orchestrator health checks.

## Safety & Control

### Rate Limiting
Throttles hot endpoints (e.g., 30 req/min on `/healthz`) to protect the database and keep latency predictable. Callers get `429 Too Many Requests` instead of timing out under load.

### Graceful Degradation
Health checks + rate limits mean the system fails fast and predictably, preventing cascading failures.

## Versioning Strategy

Stable contracts under `/api/v1/`. Breaking changes go to `/api/v2` while v1 remains live for a deprecation window. This allows downstream consumers to migrate on their schedule.

## Docker

### Compose Up
Postgres + API in one command:
```bash
docker compose up --build
```

### Volumes
- CSVs mapped read-only (`./data:/mnt/data:ro`)
- Database volume persisted (`db_data`)

### Logs & Metrics
Available immediately from containers for local development and CI:
```bash
docker compose logs -f api
curl http://localhost:8000/metrics
```

## Testing & Data Quality

### pytest (API Contract Tests)
Ensures API shape and schemas don't break downstream consumers:

```bash
# Run inside container
docker compose exec api bash -c "cd /app && PYTHONPATH=/app pytest -q"
```

**Coverage**:
- Health endpoint validation
- JSON schema contract tests
- Response structure validation

### dbt Tests (Data Quality)
Warehouse-layer validation with `not_null`, `accepted_values`, and custom checks:

```bash
# Build models and run tests
docker compose exec api bash -c "cd /app/dbt && dbt build && dbt test"
```

**Tests**:
- `not_null` on primary keys and required fields
- `accepted_values` for enums (appointment_status, traffic_source, group)
- Custom data quality rules