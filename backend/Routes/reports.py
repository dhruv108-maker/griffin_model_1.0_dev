from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pypdf import PdfReader
from sqlalchemy.orm import Session

from backend.Database.models import Project, Report
from backend.Dependencies.database_dep import get_db
from backend.Services.storage_services import StorageService

router = APIRouter(prefix="/reports", tags=["Reports"])


def _validate_pdf(file: UploadFile) -> None:
    if not file.filename or Path(file.filename).suffix.lower() != ".pdf":
        raise HTTPException(status_code=400, detail="Only PDF reports are supported")


@router.post("/upload")
async def upload_report(
    project_id: str = Form(...),
    student_name: str | None = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    _validate_pdf(file)

    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    file_path = StorageService.save_upload_file(file, subfolder=f"projects/{project_id}/reports")

    try:
        total_pages = len(PdfReader(file_path).pages)
    except Exception as exc:
        Path(file_path).unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail=f"Invalid PDF report: {exc}") from exc

    report = Report(
        project_id=project_id,
        title=file.filename,
        student_name=student_name,
        file_path=file_path,
        total_pages=total_pages,
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


@router.get("")
def list_reports(project_id: str, db: Session = Depends(get_db)):
    return (
        db.query(Report)
        .filter(Report.project_id == project_id)
        .order_by(Report.created_at.desc())
        .all()
    )


@router.get("/{report_id}")
def get_report(report_id: str, db: Session = Depends(get_db)):
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@router.delete("/{report_id}", status_code=204)
def delete_report(report_id: str, db: Session = Depends(get_db)):
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    Path(report.file_path).unlink(missing_ok=True)
    db.delete(report)
    db.commit()
