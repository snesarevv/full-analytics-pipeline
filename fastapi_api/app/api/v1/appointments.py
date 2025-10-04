from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, and_
from datetime import date
from app.core.database import get_db
from app.models.appointment import Appointment
from app.schemas.appointment import AppointmentOut

router = APIRouter(prefix="/appointments", tags=["appointments"])


@router.get("/", response_model=list[AppointmentOut])
def list_appointments(
    db: Session = Depends(get_db),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    patient_id: int | None = None,
    status: str | None = Query(None, alias="appointment_status"),
    doctor_name: str | None = None,
    reason: str | None = Query(None, alias="appointment_reason"),
    date_from: date | None = None,
    date_to: date | None = None,
):
    conds = []
    if patient_id is not None:
        conds.append(Appointment.patient_id == patient_id)
    if status:
        conds.append(Appointment.appointment_status == status)
    if doctor_name:
        conds.append(Appointment.doctor_name == doctor_name)
    if reason:
        conds.append(Appointment.appointment_reason == reason)
    if date_from:
        conds.append(Appointment.appointment_date >= date_from)
    if date_to:
        conds.append(Appointment.appointment_date <= date_to)

    stmt = select(Appointment).where(and_(*conds)) if conds else select(Appointment)
    stmt = stmt.order_by(Appointment.appointment_date, Appointment.id).offset(offset).limit(limit)
    return db.execute(stmt).scalars().all()
