from pydantic import BaseModel


class AppProfileOut(BaseModel):
    patient_id: int
    traffic_source: str | None
    device: str | None

    class Config:
        from_attributes = True
