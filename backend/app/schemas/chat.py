from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Optional


class SourceMetadata(BaseModel):
    document_id: int
    filename: str
    page: Optional[int] = None
    chunk_index: int
    similarity: float
    preview: str


class ChatRequest(BaseModel):
    conversation_id: Optional[int] = None
    message: str = Field(..., min_length=1, description="Question for the RAG assistant")


class ChatResponse(BaseModel):
    conversation_id: int
    message: str
    sources: List[SourceMetadata] = []
