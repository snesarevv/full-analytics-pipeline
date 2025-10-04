from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, and_
from app.core.database import get_db
from app.models.app_profile import AppProfile
from app.schemas.app_profile import AppProfileOut

router = APIRouter(prefix="/app_profiles", tags=["app_profiles"])


@router.get("/", response_model=list[AppProfileOut])
def list_profiles(
    db: Session = Depends(get_db),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    traffic_source: str | None = None,
    device_like: str | None = None,
):
    conds = []
    if traffic_source:
        conds.append(AppProfile.traffic_source == traffic_source)
    if device_like:
        conds.append(AppProfile.device.ilike(f"%{device_like}%"))

    stmt = select(AppProfile).where(and_(*conds)) if conds else select(AppProfile)
    stmt = stmt.order_by(AppProfile.patient_id).offset(offset).limit(limit)
    return db.execute(stmt).scalars().all()
