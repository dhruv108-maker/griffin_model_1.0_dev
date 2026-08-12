"""
backend/Schemas/settings.py
Pydantic schemas for application and Griffin evaluation settings.
"""

from typing import Optional
from pydantic import BaseModel, Field


class SettingsUpdateSchema(BaseModel):
    confidence_threshold: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Validation threshold for evidence matching"
    )
    max_concurrent_jobs: Optional[int] = Field(
        None, ge=1, le=16, description="Maximum background async job slots"
    )
    llm_validation_active: Optional[bool] = Field(
        None, description="Toggle LLM verification layer"
    )


class SettingsResponseSchema(BaseModel):
    confidence_threshold: float = 0.50
    max_concurrent_jobs: int = 4
    vector_embedding_model: str = "all-MiniLM-L6-v2"
    llm_validation_active: bool = True