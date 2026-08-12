"""
backend/Schemas/report.py
Pydantic schemas for student PDF reports.
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class ReportCreateSchema(BaseModel):
    project_id: str = Field(..., description="Parent project ID")
    title: str = Field(..., min_length=1, max_length=255, description="Report document title")
    student_name: Optional[str] = Field(None, description="Name of the student/intern")


class ReportUpdateSchema(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    student_name: Optional[str] = None


class ReportResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    title: str
    student_name: Optional[str] = None
    file_path: str
    total_pages: int
    created_at: datetime
    updated_at: datetime