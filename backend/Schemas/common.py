"""
backend/Schemas/common.py
Common/shared request and response schemas across all endpoints.
"""

from typing import Generic, TypeVar, Optional, List
from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    """Standard generic API envelope for responses."""
    success: bool = True
    message: Optional[str] = "Operation completed successfully"
    data: Optional[T] = None


class StatusResponse(BaseModel):
    """Simple status indicator schema."""
    success: bool
    message: str


class PaginationParams(BaseModel):
    """Query parameters for paginated endpoints."""
    page: int = 1
    page_size: int = 20


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated list envelope."""
    items: List[T]
    total_items: int
    page: int
    page_size: int
    total_pages: int