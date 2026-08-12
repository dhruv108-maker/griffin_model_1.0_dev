"""
backend/Services/workspace_service.py
Service handling Workspace database operations.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from backend.Database.models import Workspace, Project
from backend.Schemas.workspace import WorkspaceCreateSchema, WorkspaceUpdateSchema


class WorkspaceService:

    @staticmethod
    def list_workspaces(db: Session) -> List[Workspace]:
        return db.query(Workspace).order_by(Workspace.created_at.desc()).all()

    @staticmethod
    def get_workspace(db: Session, workspace_id: str) -> Optional[Workspace]:
        return db.query(Workspace).filter(Workspace.id == workspace_id).first()

    @staticmethod
    def create_workspace(db: Session, payload: WorkspaceCreateSchema) -> Workspace:
        ws = Workspace(
            name=payload.name,
            description=payload.description
        )
        db.add(ws)
        db.commit()
        db.refresh(ws)
        return ws

    @staticmethod
    def update_workspace(db: Session, workspace_id: str, payload: WorkspaceUpdateSchema) -> Optional[Workspace]:
        ws = WorkspaceService.get_workspace(db, workspace_id)
        if not ws:
            return None
        
        if payload.name is not None:
            ws.name = payload.name
        if payload.description is not None:
            ws.description = payload.description

        db.commit()
        db.refresh(ws)
        return ws

    @staticmethod
    def delete_workspace(db: Session, workspace_id: str) -> bool:
        ws = WorkspaceService.get_workspace(db, workspace_id)
        if not ws:
            return False
        db.delete(ws)
        db.commit()
        return True