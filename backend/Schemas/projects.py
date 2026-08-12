"""
backend/Schemas/project.py
Pydantic schemas for Project domain models.
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class ProjectCreateSchema(BaseModel):
    workspace_id: str = Field(..., description="ID of the parent workspace")
    name: str = Field(..., min_length=1, max_length=255, description="Project title")
    description: Optional[str] = Field(None, description="Detailed project description")


class ProjectUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None


class ProjectResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    workspace_id: str
    name: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class ProjectDetailResponseSchema(ProjectResponseSchema):
    total_curriculums: int = 0
    total_reports: int = 0
    total_evaluations: int = 0