# Production-Ready Analytics Pipeline Guide

This guide covers all senior-level production features implemented in this analytics pipeline.

## 🏗️ Architecture Overview

```
CSV Data → FastAPI (Seeding) → PostgreSQL
                                    ↓
                    ┌───────────────┼───────────────┐
                    ↓               ↓               ↓
                  dbt          Great Expectations  API
              (Transform)      (Data Quality)   (Serve)
                    ↓               ↓               ↓
                  Marts         Validation      Airflow/BI
```

## 📊 Components

### 1. FastAPI Application
- **Structured Logging**: JSON logs with request IDs for distributed tracing
- **Prometheus Metrics**: `/metrics` endpoint for monitoring
- **Rate Limiting**: 30 req/min on health endpoints (configurable per route)
- **Health Checks**: `/healthz` for orchestration
- **API Versioning**: `/api/v1/` namespace for future compatibility

### 2. dbt (Data Build Tool)
**Location**: `dbt/`

**Layers**:
- **Sources** (`sources.yml`): Raw tables from FastAPI seeding
- **Staging** (`models/staging/`): Type-cast, null-safe views
- **Marts** (`models/marts/`): Business-ready materialized tables

**Run**:
```bash
cd dbt
export DBT_PROFILES_DIR=$(pwd)
dbt build
```

**Models Created**:
- `stg_app_profile`, `stg_appointment`, `stg_ab_event` (views)
- `dim_patient_from_app_profiles` (table)
- `fct_appointments`, `fct_ab_events` (tables)

### 3. Great Expectations (Data Quality)
**Location**: `great_expectations/`

**Validation Suites**:
- `public__app_profile`: Non-null patient_id, traffic_source enum validation
- `public__appointment`: Non-null patient_id, status enum, date range checks
- `public__ab_event`: Non-null patient_id, group enum (Test/Control)

**Run**:
```bash
great_expectations checkpoint run postgres_tables \
  --config-directory great_expectations
```

**Checks**:
- Column nullability
- Enum value sets (with 90-95% threshold)
- Date range boundaries
- Ready for row count parity checks

### 4. pytest (API Contract Tests)
**Location**: `tests/`

**Test Suites**:
- `test_meta.py`: Health checks, count endpoints
- `test_contracts.py`: JSON schema validation for API consumers

**Run**:
```bash
pytest -v
```

**Purpose**: Ensures API contracts don't break downstream Airflow DAGs

### 5. Observability Stack

#### Structured Logging
- **Format**: JSON with ISO timestamps
- **Fields**: `request_id`, `method`, `path`, `status_code`, `duration_ms`
- **Middleware**: `RequestIdMiddleware` adds `X-Request-Id` header

#### Prometheus Metrics
- **Endpoint**: `http://localhost:8000/metrics`
- **Metrics**:
  - HTTP request duration histograms
  - Request count by status code
  - Active requests gauge
- **Integration**: Auto-instrumented via `prometheus-fastapi-instrumentator`

#### Rate Limiting
- **Library**: `slowapi`
- **Default**: 30 requests/minute on `/healthz`
- **Response**: 429 status code with JSON error
- **Extensible**: Apply `@limiter.limit()` decorator to any endpoint

## 🚀 Running the Full Stack

### Development (Local)
```bash
# Start API + DB
docker-compose up -d db api

# Run dbt transformations
docker-compose run --rm dbt

# Run Great Expectations validations
docker-compose run --rm ge

# Run tests
pytest -v
```

### Production (All Services)
```bash
docker-compose up --build
```

**Services**:
- `db`: PostgreSQL 15 with health checks
- `api`: FastAPI with metrics, logging, rate limiting
- `dbt`: Runs transformations on startup
- `ge`: Runs data quality checks on startup

## 📡 API Endpoints Reference

### Core Endpoints
- `GET /healthz` - Application health (rate limited)
- `GET /metrics` - Prometheus metrics
- `GET /api/v1/meta/health` - Database health
- `GET /api/v1/meta/counts` - Record counts

### Data Endpoints
All support pagination (`limit`, `offset`) and filtering:

- `GET /api/v1/ab_events/` - A/B test events
  - Filters: `patient_id`, `group`, `event_name`, `since`, `before`
  
- `GET /api/v1/appointments/` - Appointments
  - Filters: `patient_id`, `appointment_status`, `doctor_name`, `appointment_reason`, `date_from`, `date_to`
  
- `GET /api/v1/app_profiles/` - App profiles
  - Filters: `traffic_source`, `device_like`

## 🔍 Monitoring & Debugging

### View Logs
```bash
docker-compose logs -f api
```

**Look for**:
- `request_id`: Trace requests across services
- `duration_ms`: Identify slow endpoints
- `status_code`: Track errors

### Check Metrics
```bash
curl http://localhost:8000/metrics
```

**Key metrics**:
- `http_requests_total`: Request count
- `http_request_duration_seconds`: Latency percentiles

### Database Access
```bash
docker exec -it fastapi_api-db-1 psql -U app -d appdb
```

**Useful queries**:
```sql
-- Check row counts
SELECT 'app_profile' as tbl, count(*) FROM app_profile
UNION ALL
SELECT 'appointment', count(*) FROM appointment
UNION ALL
SELECT 'ab_event', count(*) FROM ab_event;

-- Check dbt marts
SELECT * FROM dim_patient_from_app_profiles LIMIT 5;
SELECT * FROM fct_appointments LIMIT 5;
```

## 🧪 Testing Strategy

### Unit Tests
```bash
pytest tests/test_meta.py -v
```

### Contract Tests
```bash
pytest tests/test_contracts.py -v
```

### Integration Tests
```bash
# Start services
docker-compose up -d

# Run full test suite
pytest -v

# Run dbt tests
cd dbt && dbt test
```

## 📈 Airflow Integration Pattern

```python
# Example DAG
from airflow import DAG
from airflow.operators.http_operator import SimpleHttpOperator
from airflow.operators.bash_operator import BashOperator

with DAG('analytics_pipeline', schedule_interval='@daily') as dag:
    
    # 1. Validate data quality
    validate = BashOperator(
        task_id='validate_data',
        bash_command='great_expectations checkpoint run postgres_tables'
    )
    
    # 2. Run dbt transformations
    transform = BashOperator(
        task_id='dbt_build',
        bash_command='cd /app/dbt && dbt build'
    )
    
    # 3. Extract via API
    extract = SimpleHttpOperator(
        task_id='extract_events',
        http_conn_id='analytics_api',
        endpoint='/api/v1/ab_events',
        method='GET',
        data={'limit': 1000, 'group': 'Test'}
    )
    
    validate >> transform >> extract
```

## 🔐 Production Checklist

Before deploying to production:

### Security
- [ ] Change database credentials (`.env`)
- [ ] Add JWT/OAuth2 authentication
- [ ] Enable HTTPS/TLS
- [ ] Configure CORS properly
- [ ] Set up secrets management (Vault, AWS Secrets Manager)

### Performance
- [ ] Tune PostgreSQL settings (`shared_buffers`, `work_mem`)
- [ ] Add Redis caching layer
- [ ] Configure connection pooling
- [ ] Add database read replicas
- [ ] Set up CDN for static assets

### Reliability
- [ ] Set up database backups (automated)
- [ ] Configure log aggregation (ELK, Datadog)
- [ ] Set up alerting (PagerDuty, Opsgenie)
- [ ] Add circuit breakers
- [ ] Implement retry logic with exponential backoff

### Monitoring
- [ ] Deploy Prometheus + Grafana
- [ ] Create SLO dashboards
- [ ] Set up error tracking (Sentry)
- [ ] Configure uptime monitoring
- [ ] Add custom business metrics

### Data Quality
- [ ] Add row count parity checks to GE suites
- [ ] Set up data lineage tracking
- [ ] Configure anomaly detection
- [ ] Add data freshness checks

### Database
- [ ] Migrate to Alembic for schema versioning
- [ ] Set up partitioning for large tables
- [ ] Add materialized views for heavy queries
- [ ] Configure vacuum/analyze schedules

## 🎯 API Versioning Strategy

**Current**: `/api/v1/`

**When to create v2**:
- Breaking changes to response schemas
- Removing fields
- Changing field types
- Renaming endpoints

**Migration path**:
1. Create `app/api/v2/` directory
2. Copy and modify routers
3. Add `app.include_router(v2_router, prefix="/api/v2")`
4. Maintain v1 for 6-12 months (deprecation window)
5. Document changes in API docs and README

## 📚 Additional Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **dbt Docs**: https://docs.getdbt.com/
- **Great Expectations**: https://docs.greatexpectations.io/
- **Prometheus**: https://prometheus.io/docs/
- **SQLAlchemy**: https://docs.sqlalchemy.org/

## 🤝 Contributing

When adding new features:
1. Add tests in `tests/`
2. Update API documentation
3. Add GE expectations for new tables
4. Create dbt models for new data
5. Update this guide
6. Add Prometheus metrics if needed

## 📝 License

MIT
