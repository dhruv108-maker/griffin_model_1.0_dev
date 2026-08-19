import asyncio
import json
import queue

from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from backend.Database.models import BatchJob, Evaluation, GeneratedReport, JobStatus
from backend.Dependencies.database_dep import get_db
from backend.Schemas.evaluation import (
    BatchJobResponseSchema,
    EvaluationCreateSchema,
    EvaluationResponseSchema,
    GriffinResultResponseSchema,
)
from backend.Services.evaluation_events import EvaluationEventBus
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


@router.get("/{evaluation_id}/stream")
async def stream_evaluation_status(evaluation_id: str, request: Request, db: Session = Depends(get_db)):
    evaluation = db.query(Evaluation).filter(Evaluation.id == evaluation_id).first()
    if not evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found")

    job = (
        db.query(BatchJob)
        .filter(BatchJob.evaluation_id == evaluation_id)
        .order_by(BatchJob.created_at.desc())
        .first()
    )

    channel = EvaluationEventBus.subscribe(evaluation_id)

    async def event_generator():
        try:
            if job:
                initial = {
                    "type": "status",
                    "evaluation_id": evaluation_id,
                    "status": job.status.value if hasattr(job.status, "value") else str(job.status),
                    "progress": job.progress_percentage,
                    "logs": job.logs or [],
                    "error": job.error_message,
                }
                yield f"data: {json.dumps(initial)}\n\n"

            while True:
                if await request.is_disconnected():
                    break

                try:
                    event = await asyncio.to_thread(channel.get, True, 15.0)
                except queue.Empty:
                    yield ": keep-alive\n\n"
                    continue

                yield f"data: {json.dumps(event)}\n\n"

                if event.get("status") in {"COMPLETED", "FAILED", "CANCELLED"}:
                    break
        finally:
            EvaluationEventBus.unsubscribe(evaluation_id, channel)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


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
        job.completed_at = datetime.utcnow()

    db.commit()
    EvaluationEventBus.publish(
        evaluation_id,
        {
            "type": "status",
            "evaluation_id": evaluation_id,
            "status": "CANCELLED",
            "progress": job.progress_percentage if job else 0.0,
            "logs": job.logs if job else [],
            "error": None,
        },
    )
    db.refresh(evaluation)
    return evaluation


@router.get("/{evaluation_id}/result", response_model=list[GriffinResultResponseSchema])
def get_evaluation_result(evaluation_id: str, db: Session = Depends(get_db)):
    evaluation = db.query(Evaluation).filter(Evaluation.id == evaluation_id).first()
    if not evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found")

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
