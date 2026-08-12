from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session
from backend.Dependencies.database_dep import get_db
from backend.Database.models import Curriculum
import os

router = APIRouter(prefix="/curriculum", tags=["Curriculum"])

@router.post("/upload")
async def upload_curriculum(
    project_id: str = Form(...),
    title: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    os.makedirs("/tmp/storage", exist_ok=True)
    file_path = f"/tmp/storage/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())

    curriculum = Curriculum(
        project_id=project_id,
        title=title,
        file_path=file_path
    )
    db.add(curriculum)
    db.commit()
    db.refresh(curriculum)
    return curriculum
