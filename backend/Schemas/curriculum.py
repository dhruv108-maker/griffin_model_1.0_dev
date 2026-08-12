"""
backend/Schemas/curriculum.py
Pydantic schemas for Curriculum specification models.
"""

from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class CurriculumCreateSchema(BaseModel):
    project_id: str = Field(..., description="Target project ID")
    title: str = Field(..., min_length=1, max_length=255)


class CurriculumResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    title: str
    file_path: str
    parsed_schema: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime