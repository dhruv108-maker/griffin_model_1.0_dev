from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.Dependencies.database_dep import get_db
from backend.Database.models import Evaluation

router = APIRouter(prefix="/history", tags=["History"])

@router.get("")
def get_evaluation_history(project_id: str = None, db: Session = Depends(get_db)):
    query = db.query(Evaluation)
    if project_id:
        query = query.filter(Evaluation.project_id == project_id)
    return query.order_by(Evaluation.created_at.desc()).all()