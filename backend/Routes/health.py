from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from backend.Dependencies.database_dep import get_db

router = APIRouter(prefix="/health", tags=["Health"])

@router.get("")
def check_health(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        db_status = "disconnected"

    return {
        "status": "healthy",
        "database": db_status,
        "engine": "Griffin Core v1.0 Backend"
    }