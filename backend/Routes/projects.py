from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.Database.models import Project
from backend.Dependencies.database_dep import get_db
from backend.Schemas.projects import ProjectCreateSchema, ProjectDetailResponseSchema, ProjectResponseSchema, ProjectUpdateSchema
from backend.Services.project_services import ProjectService

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.get("", response_model=list[ProjectResponseSchema])
def list_projects(workspace_id: str | None = None, db: Session = Depends(get_db)):
    return ProjectService.list_projects(db, workspace_id)


@router.post("", response_model=ProjectResponseSchema, status_code=201)
def create_project(payload: ProjectCreateSchema, db: Session = Depends(get_db)):
    try:
        return ProjectService.create_project(db, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/{project_id}", response_model=ProjectDetailResponseSchema)
def get_project(project_id: str, db: Session = Depends(get_db)):
    project = ProjectService.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return ProjectDetailResponseSchema(
        **ProjectResponseSchema.model_validate(project).model_dump(),
        total_curriculums=len(project.curriculums),
        total_reports=len(project.reports),
        total_evaluations=len(project.evaluations),
    )


@router.put("/{project_id}", response_model=ProjectResponseSchema)
def update_project(project_id: str, payload: ProjectUpdateSchema, db: Session = Depends(get_db)):
    project = ProjectService.update_project(db, project_id, payload)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.delete("/{project_id}", status_code=204)
def delete_project(project_id: str, db: Session = Depends(get_db)):
    if not ProjectService.delete_project(db, project_id):
        raise HTTPException(status_code=404, detail="Project not found")
