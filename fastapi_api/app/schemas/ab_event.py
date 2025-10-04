from pydantic import BaseModel
from datetime import datetime


class ABEventOut(BaseModel):
    id: int
    patient_id: int
    group: str | None
    event_name: str | None
    event_datetime: datetime | None

    class Config:
        from_attributes = True
