"""
backend/Schemas/chat.py
Pydantic schemas for chat sessions and conversational messages.
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class MessageCreateSchema(BaseModel):
    chat_id: str = Field(..., description="Parent chat session ID")
    content: str = Field(..., min_length=1, description="Message text payload")


class MessageResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    chat_id: str
    sender: str  # 'user' or 'assistant'
    content: str
    created_at: datetime


class ChatCreateSchema(BaseModel):
    project_id: str = Field(..., description="Associated project ID")
    evaluation_id: Optional[str] = Field(None, description="Optional evaluation context ID")
    title: str = Field(..., min_length=1, max_length=255, description="Chat session title")


class ChatResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    evaluation_id: Optional[str] = None
    title: str
    created_at: datetime
    updated_at: datetime


class ChatDetailResponseSchema(ChatResponseSchema):
    messages: List[MessageResponseSchema] = []