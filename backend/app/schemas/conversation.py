from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from app.schemas.chat import SourceMetadata


class MessageSchema(BaseModel):
    id: int
    conversation_id: int
    role: str
    content: str
    sources: Optional[List[SourceMetadata]] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ConversationCreate(BaseModel):
    title: Optional[str] = "New Conversation"


class ConversationResponse(BaseModel):
    id: int
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: Optional[int] = 0

    model_config = ConfigDict(from_attributes=True)


class ConversationDetailResponse(ConversationResponse):
    messages: List[MessageSchema] = []

