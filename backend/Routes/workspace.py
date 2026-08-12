from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.Dependencies.database_dep import get_db
from backend.Database.models import Workspace

router = APIRouter(prefix="/workspaces", tags=["Workspaces"])

@router.get("")
def workspaces(db: Session = Depends(get_db)):
    return db.query(Workspace).all()

@router.post("")
def create_workspace(name: str, description: str = None, db: Session = Depends(get_db)):
    ws = Workspace(name=name, description=description)
    db.add(ws)
    db.commit()
    db.refresh(ws)
    return ws