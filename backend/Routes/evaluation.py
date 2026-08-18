from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.Database.models import BatchJob, Evaluation, GeneratedReport, JobStatus
from backend.Dependencies.database_dep import get_db
from backend.Schemas.evaluation import (
    BatchJobResponseSchema,
    EvaluationCreateSchema,
    EvaluationResponseSchema,
    GriffinResultResponseSchema,
)
from backend.Services.evaluation_service import EvaluationService

router = APIRouter(prefix="/evaluations", tags=["Evaluations"])


@router.post("", response_model=EvaluationResponseSchema, status_code=202)
@router.post("/run", response_model=EvaluationResponseSchema, status_code=202)
def start_evaluation(
    payload: EvaluationCreateSchema,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    try:
        evaluation = EvaluationService.create_evaluation(
            db,
            payload.project_id,
            payload.curriculum_id,
            payload.name,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    background_tasks.add_task(
        EvaluationService.run_async_evaluation,
        evaluation.id,
        payload.report_ids,
    )
    return evaluation


@router.get("/{evaluation_id}", response_model=EvaluationResponseSchema)
def get_evaluation(evaluation_id: str, db: Session = Depends(get_db)):
    evaluation = db.query(Evaluation).filter(Evaluation.id == evaluation_id).first()
    if not evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    return evaluation


@router.get("/{evaluation_id}/status", response_model=BatchJobResponseSchema)
def get_job_status(evaluation_id: str, db: Session = Depends(get_db)):
    job = (
        db.query(BatchJob)
        .filter(BatchJob.evaluation_id == evaluation_id)
        .order_by(BatchJob.created_at.desc())
        .first()
    )
    if not job:
        raise HTTPException(status_code=404, detail="Evaluation job not found")
    return job


@router.post("/{evaluation_id}/cancel", response_model=EvaluationResponseSchema)
def cancel_evaluation(evaluation_id: str, db: Session = Depends(get_db)):
    evaluation = db.query(Evaluation).filter(Evaluation.id == evaluation_id).first()
    if not evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    if evaluation.status in {JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED}:
        return evaluation

    evaluation.status = JobStatus.CANCELLED
    job = (
        db.query(BatchJob)
        .filter(BatchJob.evaluation_id == evaluation_id)
        .order_by(BatchJob.created_at.desc())
        .first()
    )
    if job and job.status in {JobStatus.PENDING, JobStatus.PROCESSING}:
        job.status = JobStatus.CANCELLED
        job.completed_at = __import__("datetime").datetime.utcnow()
    db.commit()
    db.refresh(evaluation)
    return evaluation


@router.get("/{evaluation_id}/result", response_model=list[GriffinResultResponseSchema])
def get_evaluation_result(evaluation_id: str, db: Session = Depends(get_db)):
    rows = (
        db.query(GeneratedReport)
        .filter(GeneratedReport.evaluation_id == evaluation_id)
        .order_by(GeneratedReport.created_at.asc())
        .all()
    )
    if not rows:
        raise HTTPException(status_code=404, detail="No stored GriffinResults for this evaluation")
    return rows


@router.get("/{evaluation_id}/results/{report_id}", response_model=GriffinResultResponseSchema)
def get_report_result(evaluation_id: str, report_id: str, db: Session = Depends(get_db)):
    row = (
        db.query(GeneratedReport)
        .filter(
            GeneratedReport.evaluation_id == evaluation_id,
            GeneratedReport.report_id == report_id,
        )
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Stored GriffinResult not found")
    return row
