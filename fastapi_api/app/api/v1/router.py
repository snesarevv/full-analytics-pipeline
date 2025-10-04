from fastapi import APIRouter
from . import app_profiles, appointments, ab_events, meta

router = APIRouter()
router.include_router(app_profiles.router)
router.include_router(appointments.router)
router.include_router(ab_events.router)
router.include_router(meta.router)
