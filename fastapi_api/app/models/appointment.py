from sqlalchemy import String, Integer, Date, Index
from sqlalchemy.orm import Mapped, mapped_column
from datetime import date
from app.core.database import Base


class Appointment(Base):
    __tablename__ = "appointment"

    id: Mapped[int] = mapped_column(primary_key=True)  # surrogate key
    patient_id: Mapped[int] = mapped_column(index=True)
    age: Mapped[int | None] = mapped_column(Integer)
    gender: Mapped[str | None] = mapped_column(String(16), index=True)
    doctor_name: Mapped[str | None] = mapped_column(String(80), index=True)
    appointment_reason: Mapped[str | None] = mapped_column(String(120), index=True)
    appointment_date: Mapped[date | None] = mapped_column(Date, index=True)
    appointment_status: Mapped[str | None] = mapped_column(String(32), index=True)


# Useful composite index for deduping/analytics
Index(
    "ix_appt_patient_date_reason",
    Appointment.patient_id,
    Appointment.appointment_date,
    Appointment.appointment_reason
)
