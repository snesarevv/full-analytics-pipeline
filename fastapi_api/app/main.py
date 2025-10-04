from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.core.config import get_settings
from app.core.database import Base, engine, SessionLocal
from app.api.v1.router import router as api_v1_router
from app.services.seed import seed
from app.core.logging import setup_logging, RequestIdMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

settings = get_settings()

# Setup structured logging
setup_logging()

# Initialize FastAPI app
app = FastAPI(title=settings.APP_NAME)

# Add middleware
app.add_middleware(RequestIdMiddleware)

# Setup rate limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
def ratelimit_handler(request, exc):
    return JSONResponse(status_code=429, content={"detail": "rate limit exceeded"})


# Add SlowAPI middleware
app.add_middleware(SlowAPIMiddleware)

# Include API routers
app.include_router(api_v1_router, prefix=settings.API_V1_PREFIX)

# Setup Prometheus instrumentation BEFORE startup
instrumentator = Instrumentator(
    should_group_status_codes=True,
    should_ignore_untemplated=True
)
instrumentator.instrument(app)
instrumentator.expose(app, endpoint="/metrics")


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)   # Alembic recommended later
    if settings.AUTO_SEED:
        with SessionLocal() as db:
            seed(db)


@app.get("/healthz")
@limiter.limit("30/minute")
def healthz(request: Request):
    return {"status": "ok"}
