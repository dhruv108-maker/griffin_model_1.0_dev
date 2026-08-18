"""Project domain operations."""

from typing import List, Optional

from sqlalchemy.orm import Session

from backend.Database.models import Project, Workspace
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
        workspace = db.query(Workspace).filter(Workspace.id == payload.workspace_id).first()
        if workspace is None:
            raise ValueError("Workspace not found")

        project = Project(
            workspace_id=payload.workspace_id,
            name=payload.name.strip(),
            description=payload.description,
        )
        db.add(project)
        db.commit()
        db.refresh(project)
        return project

    @staticmethod
    def update_project(db: Session, project_id: str, payload: ProjectUpdateSchema) -> Optional[Project]:
        project = ProjectService.get_project(db, project_id)
        if project is None:
            return None

        if payload.name is not None:
            project.name = payload.name.strip()
        if payload.description is not None:
            project.description = payload.description

        db.commit()
        db.refresh(project)
        return project

    @staticmethod
    def delete_project(db: Session, project_id: str) -> bool:
        project = ProjectService.get_project(db, project_id)
        if project is None:
            return False
        db.delete(project)
        db.commit()
        return True
