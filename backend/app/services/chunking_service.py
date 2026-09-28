from typing import List, Dict, Any
from app.core.config import settings
from app.core.logging_config import logger


class ChunkingService:
    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        self.chunk_size = chunk_size or settings.CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP

    def chunk_extracted_pages(
        self,
        extracted_pages: List[Dict[str, Any]],
        document_id: int,
        filename: str
    ) -> List[Dict[str, Any]]:
        """
        Takes extracted page items `[{"text": "...", "page": int|None}, ...]`
        and produces chunk dicts with metadata and deterministic IDs.
        """
        chunks = []
        global_chunk_index = 0

        for page_data in extracted_pages:
            text = page_data.get("text", "")
            page_num = page_data.get("page")
            
            words = text.split()
            if not words:
                continue

            # If page text is within chunk size limit, take it directly
            if len(words) <= self.chunk_size:
                chunk_id = f"document_{document_id}_chunk_{global_chunk_index}"
                chunks.append({
                    "id": chunk_id,
                    "text": text,
                    "metadata": {
                        "document_id": document_id,
                        "filename": filename,
                        "page": page_num if page_num is not None else 1,
                        "chunk_index": global_chunk_index
                    }
                })
                global_chunk_index += 1
            else:
                # Sliding window chunking with word overlap
                step = self.chunk_size - self.chunk_overlap
                if step <= 0:
                    step = self.chunk_size // 2

                for start in range(0, len(words), step):
                    end = start + self.chunk_size
                    chunk_words = words[start:end]
                    if not chunk_words:
                        break
                    
                    chunk_text = " ".join(chunk_words)
                    chunk_id = f"document_{document_id}_chunk_{global_chunk_index}"
                    
                    chunks.append({
                        "id": chunk_id,
                        "text": chunk_text,
                        "metadata": {
                            "document_id": document_id,
                            "filename": filename,
                            "page": page_num if page_num is not None else 1,
                            "chunk_index": global_chunk_index
                        }
                    })
                    global_chunk_index += 1

                    if end >= len(words):
                        break

        logger.info(f"Chunked document_id={document_id} filename='{filename}' into {len(chunks)} chunks.")
        return chunks
