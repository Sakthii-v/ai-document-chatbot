from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Optional


class DocumentBase(BaseModel):
    filename: str
    file_type: str
    file_size: int


class DocumentCreate(DocumentBase):
    file_hash: str
    chunk_count: int = 0


class DocumentResponse(DocumentBase):
    id: int
    file_hash: str
    status: str
    chunk_count: int
    created_at: datetime
    message: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)



class DocumentUploadResponse(BaseModel):
    id: int
    filename: str
    status: str
    chunk_count: int
    message: str
    is_duplicate: bool = False
