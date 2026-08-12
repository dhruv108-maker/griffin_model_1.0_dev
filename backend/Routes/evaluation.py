from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from typing import List

from backend.Dependencies.database_dep import get_db
from backend.Schemas.evaluation import EvaluationCreateSchema, EvaluationResponseSchema, BatchJobResponseSchema
from backend.Services.evaluation_service import EvaluationService
from backend.Database.models import Evaluation, BatchJob, GeneratedReport

router = APIRouter(prefix="/evaluations", tags=["Evaluations"])

@router.post("", response_model=EvaluationResponseSchema)
@router.post("/run", response_model=EvaluationResponseSchema)
def start_evaluation(
    payload: EvaluationCreateSchema,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    eval_obj = EvaluationService.create_evaluation(
        db, payload.project_id, payload.curriculum_id, payload.name
    )

    # Execute async pipeline in background task
    background_tasks.add_task(
        EvaluationService.run_async_evaluation,
        eval_obj.id,
        payload.report_ids
    )

    return eval_obj

@router.get("/{evaluation_id}/status", response_model=BatchJobResponseSchema)
def get_job_status(evaluation_id: str, db: Session = Depends(get_db)):
    job = db.query(BatchJob).filter(BatchJob.evaluation_id == evaluation_id).order_by(BatchJob.created_at.desc()).first()
    if not job:
        raise HTTPException(status_code=404, detail="Evaluation job not found")
    return job

@router.get("/{evaluation_id}/result")
def get_evaluation_result(evaluation_id: str, db: Session = Depends(get_db)):
    reports = db.query(GeneratedReport).filter(GeneratedReport.evaluation_id == evaluation_id).all()
    if not reports:
        raise HTTPException(status_code=404, detail="Results not generated or job still pending")
    
    return {
        "evaluation_id": evaluation_id,
        "results": [r.griffin_result for r in reports]
    }