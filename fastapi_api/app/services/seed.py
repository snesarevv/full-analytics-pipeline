import csv
from datetime import datetime, date
from pathlib import Path
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.app_profile import AppProfile
from app.models.appointment import Appointment
from app.models.ab_event import ABEvent

settings = get_settings()
DATA_DIR = Path(settings.DATA_DIR)


def _parse_date(s: str | None) -> date | None:
    if not s or str(s).strip() == "":
        return None
    return datetime.strptime(str(s), "%Y-%m-%d").date()


def _parse_dt(s: str | None) -> datetime | None:
    if not s or str(s).strip() == "":
        return None
    # e.g. "2023-07-05 23:47:28"
    return datetime.strptime(str(s), "%Y-%m-%d %H:%M:%S")


def seed(db: Session):
    seed_app_profiles(db, DATA_DIR / "app_data.csv")
    seed_appointments(db, DATA_DIR / "appointments_data.csv")
    seed_ab_events(db, DATA_DIR / "ab_test_data.csv")


def seed_app_profiles(db: Session, path: Path):
    if not path.exists():
        return
    # upsert by patient_id
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            pid = int(row["patient_id"])
            obj = db.get(AppProfile, pid)
            if obj:
                obj.traffic_source = row.get("traffic_source") or None
                obj.device = row.get("device") or None
            else:
                db.add(AppProfile(
                    patient_id=pid,
                    traffic_source=row.get("traffic_source") or None,
                    device=row.get("device") or None,
                ))
    db.commit()


def seed_appointments(db: Session, path: Path):
    if not path.exists():
        return
    # naive idempotency: skip if exact row already exists (patient_id+date+reason)
    # fast existence map:
    existing = set(
        db.execute(
            select(Appointment.patient_id, Appointment.appointment_date, Appointment.appointment_reason)
        ).all()
    )
    to_add = []
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            key = (
                int(row["patient_id"]),
                _parse_date(row.get("appointment_date")),
                row.get("appointment_reason") or None,
            )
            if key in existing:
                continue
            to_add.append(Appointment(
                patient_id=int(row["patient_id"]),
                age=int(row["age"]) if row.get("age") not in (None, "",) else None,
                gender=row.get("gender") or None,
                doctor_name=row.get("doctor_name") or None,
                appointment_reason=row.get("appointment_reason") or None,
                appointment_date=_parse_date(row.get("appointment_date")),
                appointment_status=row.get("appointment_status") or None,
            ))
    if to_add:
        db.bulk_save_objects(to_add)
        db.commit()


def seed_ab_events(db: Session, path: Path):
    if not path.exists():
        return
    # unique composite index will drop duplicates; here we check to avoid exceptions
    existing = set(
        db.execute(
            select(ABEvent.patient_id, ABEvent.event_name, ABEvent.event_datetime)
        ).all()
    )
    to_add = []
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            pid = int(row["patient_id"])
            ev = row.get("event_name") or None
            ts = _parse_dt(row.get("event_datetime"))
            key = (pid, ev, ts)
            if key in existing:
                continue
            to_add.append(ABEvent(
                patient_id=pid,
                group=row.get("group") or None,
                event_name=ev,
                event_datetime=ts,
            ))
    if to_add:
        db.bulk_save_objects(to_add)
        db.commit()
