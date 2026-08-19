from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pypdf import PdfReader
from sqlalchemy.orm import Session

from backend.Database.models import Curriculum, Project
from backend.Dependencies.database_dep import get_db
from backend.KnowledgeBase.knowledge_evidence import CurriculumEvidenceExtractor
from backend.KnowledgeBase.curriculum_normalizer import normalize_curriculum_tree
from backend.Services.storage_services import StorageService

router = APIRouter(prefix="/curriculum", tags=["Curriculum"])


def _validate_pdf(file: UploadFile) -> None:
    if not file.filename or Path(file.filename).suffix.lower() != ".pdf":
        raise HTTPException(status_code=400, detail="Only PDF curricula are supported")


@router.post("/upload")
async def upload_curriculum(
    project_id: str = Form(...),
    title: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    _validate_pdf(file)

    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    file_path = StorageService.save_upload_file(
        file,
        subfolder=f"projects/{project_id}/curricula",
    )

    try:
        PdfReader(file_path)
    except Exception as exc:
        Path(file_path).unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail=f"Invalid curriculum PDF: {exc}") from exc

    try:
        raw_schema = CurriculumEvidenceExtractor().parse_pdf(file_path)
        parsed_schema = normalize_curriculum_tree(raw_schema)
    except Exception as exc:
        Path(file_path).unlink(missing_ok=True)
        raise HTTPException(status_code=422, detail=f"Curriculum parsing failed: {exc}") from exc

    if not parsed_schema or not parsed_schema.get("roots"):
        Path(file_path).unlink(missing_ok=True)
        raise HTTPException(status_code=422, detail="Curriculum parsing produced no structural content")

    curriculum = Curriculum(
        project_id=project_id,
        title=title.strip() or Path(file.filename).stem,
        file_path=file_path,
        parsed_schema=parsed_schema,
    )
    db.add(curriculum)
    db.commit()
    db.refresh(curriculum)
    return curriculum


@router.get("")
def list_curricula(project_id: str, db: Session = Depends(get_db)):
    return (
        db.query(Curriculum)
        .filter(Curriculum.project_id == project_id)
        .order_by(Curriculum.created_at.desc())
        .all()
    )


@router.get("/{curriculum_id}")
def get_curriculum(curriculum_id: str, db: Session = Depends(get_db)):
    curriculum = db.query(Curriculum).filter(Curriculum.id == curriculum_id).first()
    if not curriculum:
        raise HTTPException(status_code=404, detail="Curriculum not found")
    return curriculum


@router.delete("/{curriculum_id}", status_code=204)
def delete_curriculum(curriculum_id: str, db: Session = Depends(get_db)):
    curriculum = db.query(Curriculum).filter(Curriculum.id == curriculum_id).first()
    if not curriculum:
        raise HTTPException(status_code=404, detail="Curriculum not found")

    Path(curriculum.file_path).unlink(missing_ok=True)
    db.delete(curriculum)
    db.commit()
