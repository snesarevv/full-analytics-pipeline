from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_
from datetime import datetime
from app.core.database import get_db
from app.models.ab_event import ABEvent
from app.schemas.ab_event import ABEventOut
from app.schemas.common import Page

router = APIRouter(prefix="/ab_events", tags=["ab_events"])


@router.get("/", response_model=list[ABEventOut])
def list_ab_events(
    db: Session = Depends(get_db),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    patient_id: int | None = None,
    group: str | None = None,
    event_name: str | None = None,
    since: datetime | None = None,
    before: datetime | None = None,
):
    conds = []
    if patient_id is not None:
        conds.append(ABEvent.patient_id == patient_id)
    if group:
        conds.append(ABEvent.group == group)
    if event_name:
        conds.append(ABEvent.event_name == event_name)
    if since:
        conds.append(ABEvent.event_datetime >= since)
    if before:
        conds.append(ABEvent.event_datetime < before)

    stmt = select(ABEvent).where(and_(*conds)) if conds else select(ABEvent)
    stmt = stmt.order_by(ABEvent.event_datetime).offset(offset).limit(limit)
    return db.execute(stmt).scalars().all()


@router.get("/page", response_model=Page)
def page_info(
    db: Session = Depends(get_db),
    patient_id: int | None = None,
    group: str | None = None,
    event_name: str | None = None,
):
    conds = []
    if patient_id is not None:
        conds.append(ABEvent.patient_id == patient_id)
    if group:
        conds.append(ABEvent.group == group)
    if event_name:
        conds.append(ABEvent.event_name == event_name)
    
    total = db.scalar(select(func.count()).select_from(ABEvent).where(*conds)) if conds \
            else db.scalar(select(func.count()).select_from(ABEvent))
    return {"limit": 0, "offset": 0, "total": total or 0}
