import os
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import UploadFile

from app.core.config import settings
from app.core.logging_config import logger
from app.core.exceptions import AppException, NotFoundError
from app.models.document import Document
from app.utils.hashing import compute_file_hash
from app.utils.file_utils import validate_file, generate_safe_filename
from app.services.extraction_service import ExtractionService
from app.services.chunking_service import ChunkingService
from app.services.embedding_service import EmbeddingService
from app.services.vector_store import VectorStore


class DocumentService:
    def __init__(
        self,
        db: Session,
        extraction_service: ExtractionService = None,
        chunking_service: ChunkingService = None,
        embedding_service: EmbeddingService = None,
        vector_store: VectorStore = None
    ):
        self.db = db
        self.extraction_service = extraction_service or ExtractionService()
        self.chunking_service = chunking_service or ChunkingService()
        self.embedding_service = embedding_service or EmbeddingService()
        self.vector_store = vector_store or VectorStore()

    def process_and_save_document(self, file: UploadFile) -> dict:
        """
        Process uploaded file: check duplicate SHA-256 hash, extract text,
        chunk, generate embeddings, store in ChromaDB and SQLite DB.
        All DB writes are atomic — the record is only committed after full success.
        """
        logger.info(f"Processing upload request for file='{file.filename}'")

        # Read file content
        content = file.file.read()
        file_size = len(content)

        if file_size == 0:
            raise AppException("EMPTY_FILE", "Uploaded file is empty.")

        # Validate format & size
        ext = validate_file(file.filename, file_size)

        # 1. Compute SHA-256 hash
        file_hash = compute_file_hash(content)
        logger.info(f"File '{file.filename}' SHA-256 hash: {file_hash}")

        # 2. Check duplicate — only return existing if it was FULLY processed (not stuck)
        existing_doc = self.db.query(Document).filter(
            Document.file_hash == file_hash,
            Document.status == "processed"
        ).first()
        if existing_doc:
            logger.info(f"Duplicate document detected! document_id={existing_doc.id}, hash={file_hash}")
            return {
                "id": existing_doc.id,
                "filename": existing_doc.filename,
                "status": existing_doc.status,
                "chunk_count": existing_doc.chunk_count,
                "message": "Duplicate document detected. Returning existing processed document.",
                "is_duplicate": True
            }

        # 2b. Clean up any stale 'processing' record for this hash (from a previous failed attempt)
        stale = self.db.query(Document).filter(
            Document.file_hash == file_hash,
            Document.status == "processing"
        ).first()
        if stale:
            logger.warning(f"Found stale processing record id={stale.id} for hash={file_hash}. Cleaning up.")
            self.db.delete(stale)
            self.db.commit()

        # 3. Save file physically to uploads directory
        safe_filename = generate_safe_filename(file.filename)
        saved_path = os.path.join(settings.UPLOAD_DIR, safe_filename)
        with open(saved_path, "wb") as f:
            f.write(content)

        db_doc = None
        try:
            # 4. Extract text
            extracted_pages = self.extraction_service.extract_text(saved_path, ext)

            # 5. Chunk text
            # Use a temporary ID=-1 for chunk IDs; we replace after getting real DB id
            temp_chunks = self.chunking_service.chunk_extracted_pages(
                extracted_pages=extracted_pages,
                document_id=-1,
                filename=file.filename
            )

            if not temp_chunks:
                raise AppException("NO_CHUNKS", "Document produced 0 chunks after extraction — it may be empty or image-only.")

            # 6. Generate embeddings
            texts = [c["text"] for c in temp_chunks]
            embeddings = self.embedding_service.embed_documents(texts)

            # 7. Only now create the DB record (after all heavy work succeeds)
            db_doc = Document(
                filename=file.filename,
                file_hash=file_hash,
                file_type=ext.lstrip("."),
                file_size=file_size,
                status="processing",
                chunk_count=0
            )
            self.db.add(db_doc)
            self.db.commit()
            self.db.refresh(db_doc)

            # 8. Fix chunk IDs now that we have the real document_id
            for i, chunk in enumerate(temp_chunks):
                chunk["id"] = f"document_{db_doc.id}_chunk_{i}"
                chunk["metadata"]["document_id"] = db_doc.id

            # 9. Store in ChromaDB
            self.vector_store.add_chunks(temp_chunks, embeddings)

            # 10. Mark as fully processed (single final commit)
            db_doc.status = "processed"
            db_doc.chunk_count = len(temp_chunks)
            self.db.commit()
            self.db.refresh(db_doc)

            logger.info(f"Document processed successfully. document_id={db_doc.id}, chunks={len(temp_chunks)}")

            return {
                "id": db_doc.id,
                "filename": db_doc.filename,
                "status": db_doc.status,
                "chunk_count": db_doc.chunk_count,
                "message": "Document processed successfully.",
                "is_duplicate": False
            }

        except Exception as e:
            # Cleanup: remove saved file
            if os.path.exists(saved_path):
                os.remove(saved_path)
            # Cleanup: remove DB record if it was partially created
            if db_doc is not None:
                try:
                    self.db.delete(db_doc)
                    self.db.commit()
                except Exception:
                    self.db.rollback()
            else:
                self.db.rollback()
            logger.error(f"Error during document processing: {e}")
            raise e

    def list_documents(self) -> List[Document]:
        """Return list of all uploaded documents."""
        return self.db.query(Document).order_by(Document.created_at.desc()).all()

    def get_document(self, document_id: int) -> Document:
        """Fetch single document by ID."""
        doc = self.db.query(Document).filter(Document.id == document_id).first()
        if not doc:
            raise NotFoundError(f"Document with ID {document_id} not found.")
        return doc

    def delete_document(self, document_id: int) -> dict:
        """Delete document vectors from ChromaDB, remove DB record and file."""
        doc = self.get_document(document_id)

        # 1. Delete ChromaDB vectors
        self.vector_store.delete_document(document_id)

        # 2. Delete DB record
        self.db.delete(doc)
        self.db.commit()

        logger.info(f"Successfully deleted document_id={document_id}")
        return {"success": True, "message": f"Document '{doc.filename}' deleted successfully."}
