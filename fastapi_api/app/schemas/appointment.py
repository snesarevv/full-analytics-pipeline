from pydantic import BaseModel
from datetime import date


class AppointmentOut(BaseModel):
    id: int
    patient_id: int
    age: int | None
    gender: str | None
    doctor_name: str | None
    appointment_reason: str | None
    appointment_date: date | None
    appointment_status: str | None

    class Config:
        from_attributes = True
