from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import get_db

router = APIRouter(prefix="/meta", tags=["meta"])


@router.get("/health")
def health(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "ok"}


@router.get("/counts")
def counts(db: Session = Depends(get_db)):
    res = {}
    for tbl in ("app_profile", "appointment", "ab_event"):
        res[tbl] = db.execute(text(f"SELECT count(*) FROM {tbl}")).scalar()
    return res
