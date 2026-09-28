from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.document import DocumentResponse, DocumentUploadResponse
from app.services.document_service import DocumentService

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("/upload", response_model=DocumentUploadResponse, status_code=status.HTTP_201_CREATED, summary="Upload document (PDF/TXT/DOCX)")
def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload PDF, TXT, or DOCX document.
    Calculates SHA-256 hash to detect duplicates and skips re-processing if duplicate.
    """
    service = DocumentService(db)
    result = service.process_and_save_document(file)
    return result


@router.get("", response_model=List[DocumentResponse], summary="List all processed documents")
def list_documents(db: Session = Depends(get_db)):
    """Retrieve all uploaded documents and their processing status."""
    service = DocumentService(db)
    return service.list_documents()


@router.get("/{document_id}", response_model=DocumentResponse, summary="Get single document details")
def get_document(document_id: int, db: Session = Depends(get_db)):
    """Get metadata for a specific document."""
    service = DocumentService(db)
    return service.get_document(document_id)


@router.delete("/{document_id}", summary="Delete a document and clean up vectors")
def delete_document(document_id: int, db: Session = Depends(get_db)):
    """Deletes document vectors from ChromaDB and removes DB record."""
    service = DocumentService(db)
    return service.delete_document(document_id)
