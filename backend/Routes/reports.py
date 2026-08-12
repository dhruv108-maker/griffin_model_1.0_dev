from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session
from backend.Dependencies.database_dep import get_db
from backend.Database.models import Report

import os

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.post("/upload")
async def upload_report(
    project_id: str = Form(...),
    student_name: str = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    os.makedirs("/tmp/storage", exist_ok=True)
    file_path = f"/tmp/storage/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())

    report = Report(
        project_id=project_id,
        title=file.filename,
        student_name=student_name,
        file_path=file_path,
        total_pages=10
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report