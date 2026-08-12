"""
backend/Schemas/workspace.py
Pydantic schemas for Workspace domain models.
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class WorkspaceCreateSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Name of the workspace")
    description: Optional[str] = Field(None, description="Optional workspace description")


class WorkspaceUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None


class WorkspaceResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    description: Optional[str] = None
    owner_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class WorkspaceDetailResponseSchema(WorkspaceResponseSchema):
    project_count: int = 0