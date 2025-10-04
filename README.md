# Full Analytics Pipeline

End-to-end analytics pipeline for healthcare data with FastAPI, PostgreSQL, and ready for Airflow/dbt integration.

## 🏗️ Architecture

This project provides a production-ready analytics infrastructure:

1. **FastAPI REST API** - Exposes healthcare analytics data with filtering and pagination
2. **PostgreSQL Database** - Stores three core datasets with proper indexing
3. **Automatic CSV Seeding** - Idempotent data loading on startup
4. **Docker Compose** - One-command deployment

## 📦 Components

### FastAPI Application (`fastapi_api/`)

RESTful API that serves three datasets:
- **A/B Test Events** - Patient engagement tracking
- **App Profiles** - User acquisition data
- **Appointments** - Healthcare appointment records

See [`fastapi_api/README.md`](fastapi_api/README.md) for detailed documentation.

## 🚀 Quick Start

```bash
# Navigate to the FastAPI directory
cd fastapi_api

# Copy environment configuration
cp .env.example .env

# Start the application (PostgreSQL + FastAPI)
docker-compose up --build
```

Access the API:
- **Interactive Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/healthz
- **Metadata**: http://localhost:8000/api/v1/meta/counts

## 📊 Data Flow

```
CSV Files (/mnt/data/)
    ↓
FastAPI Seeding Service (idempotent)
    ↓
PostgreSQL Database
    ↓
REST API Endpoints
    ↓
Airflow/dbt/BI Tools
```

## 🔧 Next Steps

This foundation is ready for:

1. **Airflow Integration** - Schedule ETL jobs
2. **dbt Models** - Build transformation layers
3. **Great Expectations** - Data quality validation
4. **BI Tools** - Connect Tableau, Metabase, etc.

## 📁 Project Structure

```
full-analytics-pipeline/
├── fastapi_api/              # FastAPI application
│   ├── app/
│   │   ├── core/            # Config & database
│   │   ├── models/          # SQLAlchemy models
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── services/        # Business logic
│   │   ├── api/v1/          # API routes
│   │   └── main.py          # App entrypoint
│   ├── docker-compose.yml
│   ├── Dockerfile
│   └── requirements.txt
└── README.md                 # This file
```

## 🎯 Features

- ✅ **Production-ready FastAPI** with proper project structure
- ✅ **Automatic database migrations** on startup
- ✅ **Idempotent CSV seeding** - safe to restart
- ✅ **Comprehensive filtering** on all endpoints
- ✅ **Pagination support** with configurable limits
- ✅ **Proper indexing** for query performance
- ✅ **Health checks** for monitoring
- ✅ **Docker Compose** for easy deployment
- ✅ **OpenAPI documentation** auto-generated

## 📝 License

MIT