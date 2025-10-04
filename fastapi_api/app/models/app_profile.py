from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class AppProfile(Base):
    __tablename__ = "app_profile"

    patient_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    traffic_source: Mapped[str | None] = mapped_column(String(80), index=True)
    device: Mapped[str | None] = mapped_column(String(80), index=True)
