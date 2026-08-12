from pydantic import BaseModel, ConfigDict
from typing import Optional, Any, Dict
from datetime import datetime
from backend.Database.models import JobStatus

class EvaluationCreateSchema(BaseModel):
    project_id: str
    curriculum_id: str
    report_ids: list[str]
    name: str

class BatchJobResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    evaluation_id: str
    status: JobStatus
    progress_percentage: float
    error_message: Optional[str] = None
    logs: Optional[Any] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

class EvaluationResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    curriculum_id: str
    name: str
    status: JobStatus
    created_at: datetime

class GriffinResultResponseSchema(BaseModel):
    evaluation_id: str
    report_id: str
    griffin_result: Dict[str, Any]