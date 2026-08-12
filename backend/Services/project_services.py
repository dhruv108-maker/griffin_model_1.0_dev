"""
backend/Services/project_service.py
Service handling Project database operations.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from backend.Database.models import Project, Curriculum, Report, Evaluation
from backend.Schemas.projects import ProjectCreateSchema, ProjectUpdateSchema


class ProjectService:

    @staticmethod
    def list_projects(db: Session, workspace_id: Optional[str] = None) -> List[Project]:
        query = db.query(Project)
        if workspace_id:
            query = query.filter(Project.workspace_id == workspace_id)
        return query.order_by(Project.created_at.desc()).all()

    @staticmethod
    def get_project(db: Session, project_id: str) -> Optional[Project]:
        return db.query(Project).filter(Project.id == project_id).first()

    @staticmethod
    def create_project(db: Session, payload: ProjectCreateSchema) -> Project:
        proj = Project(
            workspace_id=payload.workspace_id,
            name=payload.name,
            description=payload.description
        )
        db.add(proj)
        db.commit()
        db.refresh(proj)
        return proj

    @staticmethod
    def update_project(db: Session, project_id: str, payload: ProjectUpdateSchema) -> Optional[Project]:
        proj = ProjectService.get_project(db, project_id)
        if not proj:
            return None

        if payload.name is not None:
            proj.name = payload.name
        if payload.description is not None:
            proj.description = payload.description

        db.commit()
        db.refresh(proj)
        return proj

    @staticmethod
    def delete_project(db: Session, project_id: str) -> bool:
        proj = ProjectService.get_project(db, project_id)
        if not proj:
            return False
        db.delete(proj)
        db.commit()
        return True