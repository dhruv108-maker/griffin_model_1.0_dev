from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pypdf import PdfReader
from sqlalchemy.orm import Session

from backend.Database.models import Curriculum
from backend.Dependencies.database_dep import get_db


router = APIRouter(prefix="/curriculum", tags=["Curriculum"])
STORAGE_ROOT = Path("/tmp/storage")


@router.post("/upload")
async def upload_curriculum(
    project_id: str = Form(...),
    title: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Curriculum must be a PDF file")

    STORAGE_ROOT.mkdir(parents=True, exist_ok=True)
    stored_path = STORAGE_ROOT / f"{uuid4().hex}.pdf"

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded curriculum is empty")

    stored_path.write_bytes(content)

    try:
        PdfReader(str(stored_path))
    except Exception as exc:
        stored_path.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail=f"Invalid PDF: {exc}") from exc

    curriculum = Curriculum(
        project_id=project_id,
        title=title or file.filename,
        file_path=str(stored_path),
    )
    db.add(curriculum)
    db.commit()
    db.refresh(curriculum)
    return curriculum
