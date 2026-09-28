import os
from typing import List, Dict, Any
import pymupdf as fitz  # PyMuPDF
import docx
from app.core.logging_config import logger
from app.core.exceptions import DocumentProcessingError



class ExtractionService:
    @staticmethod
    def extract_pdf(file_path: str) -> List[Dict[str, Any]]:
        """Extract text from PDF preserving 1-indexed page numbers."""
        results = []
        try:
            doc = fitz.open(file_path)
            if doc.page_count == 0:
                raise DocumentProcessingError("PDF file contains no pages.")
            
            for page_index in range(len(doc)):
                page = doc.load_page(page_index)
                text = page.get_text("text").strip()
                if text:
                    results.append({
                        "text": text,
                        "page": page_index + 1  # 1-indexed
                    })
            doc.close()
        except Exception as e:
            if isinstance(e, DocumentProcessingError):
                raise e
            logger.error(f"Error extracting PDF {file_path}: {e}")
            raise DocumentProcessingError(f"Failed to process PDF file: {str(e)}")
            
        if not results:
            raise DocumentProcessingError("No readable text found in PDF file.")
        return results

    @staticmethod
    def extract_docx(file_path: str) -> List[Dict[str, Any]]:
        """Extract text from DOCX file."""
        try:
            doc = docx.Document(file_path)
            paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
            full_text = "\n\n".join(paragraphs)
            if not full_text:
                raise DocumentProcessingError("DOCX file contains no readable text.")
            
            return [{
                "text": full_text,
                "page": None
            }]
        except Exception as e:
            if isinstance(e, DocumentProcessingError):
                raise e
            logger.error(f"Error extracting DOCX {file_path}: {e}")
            raise DocumentProcessingError(f"Failed to process DOCX file: {str(e)}")

    @staticmethod
    def extract_txt(file_path: str) -> List[Dict[str, Any]]:
        """Extract text from plain text file."""
        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                text = f.read().strip()
            if not text:
                raise DocumentProcessingError("TXT file is empty.")
            
            return [{
                "text": text,
                "page": None
            }]
        except Exception as e:
            if isinstance(e, DocumentProcessingError):
                raise e
            logger.error(f"Error extracting TXT {file_path}: {e}")
            raise DocumentProcessingError(f"Failed to process TXT file: {str(e)}")

    @classmethod
    def extract_text(cls, file_path: str, file_type: str) -> List[Dict[str, Any]]:
        ext = os.path.splitext(file_path)[1].lower() or f".{file_type.lower()}"
        if ext == ".pdf":
            return cls.extract_pdf(file_path)
        elif ext == ".docx":
            return cls.extract_docx(file_path)
        elif ext == ".txt":
            return cls.extract_txt(file_path)
        else:
            raise DocumentProcessingError(f"Unsupported file extension: {ext}")
