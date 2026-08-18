from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pypdf import PdfReader
from sqlalchemy.orm import Session

from backend.Database.models import Report
from backend.Dependencies.database_dep import get_db


router = APIRouter(prefix="/reports", tags=["Reports"])
STORAGE_ROOT = Path("/tmp/storage")


@router.post("/upload")
async def upload_report(
    project_id: str = Form(...),
    student_name: str | None = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Student report must be a PDF file")

    STORAGE_ROOT.mkdir(parents=True, exist_ok=True)
    stored_path = STORAGE_ROOT / f"{uuid4().hex}.pdf"

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded report is empty")

    stored_path.write_bytes(content)

    try:
        reader = PdfReader(str(stored_path))
        total_pages = len(reader.pages)
    except Exception as exc:
        stored_path.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail=f"Invalid PDF: {exc}") from exc

    report = Report(
        project_id=project_id,
        title=file.filename,
        student_name=student_name,
        file_path=str(stored_path),
        total_pages=total_pages,
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report
