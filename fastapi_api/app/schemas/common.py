from pydantic import BaseModel
from datetime import datetime, date


class Page(BaseModel):
    limit: int
    offset: int
    total: int
