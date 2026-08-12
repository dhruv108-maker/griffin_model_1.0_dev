from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.Dependencies.database_dep import get_db
from backend.Database.models import Project
from backend.Schemas.projects import ProjectCreateSchema, ProjectResponseSchema
from backend.Services.project_services import ProjectService

router = APIRouter(prefix="/projects", tags=["Projects"])

@router.get("", response_model=list[ProjectResponseSchema])
def list_projects(workspace_id: str = None, db: Session = Depends(get_db)):
    query = db.query(Project)
    if workspace_id:
        query = query.filter(Project.workspace_id == workspace_id)
    return query.all()

@router.post("", response_model=ProjectResponseSchema)
def create_project(payload: ProjectCreateSchema, db: Session = Depends(get_db)):
    return ProjectService.create_project(db, payload)