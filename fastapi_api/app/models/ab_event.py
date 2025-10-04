from sqlalchemy import String, Integer, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from app.core.database import Base


class ABEvent(Base):
    __tablename__ = "ab_event"

    id: Mapped[int] = mapped_column(primary_key=True)
    patient_id: Mapped[int] = mapped_column(Integer, index=True)
    group: Mapped[str | None] = mapped_column(String(16), index=True)  # e.g. Test/Control
    event_name: Mapped[str | None] = mapped_column(String(64), index=True)
    event_datetime: Mapped[datetime | None] = mapped_column(DateTime, index=True)


Index("ix_ab_event_unique", ABEvent.patient_id, ABEvent.event_name, ABEvent.event_datetime, unique=True)
