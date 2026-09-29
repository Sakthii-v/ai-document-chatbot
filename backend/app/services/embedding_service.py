from typing import List
import chromadb.utils.embedding_functions as ef
from app.core.logging_config import logger


class EmbeddingService:
    """
    Uses ChromaDB's built-in ONNX DefaultEmbeddingFunction (all-MiniLM-L6-v2).
    No PyTorch required — runs in ~80MB RAM, fits Render free tier (512MB).
    """
    _instance = None
    _embed_func = None

    def __init__(self):
        if EmbeddingService._embed_func is None:
            logger.info("Initializing ChromaDB ONNX DefaultEmbeddingFunction (all-MiniLM-L6-v2)...")
            try:
                default_fn = ef.DefaultEmbeddingFunction()
                # Warm up to trigger ONNX model download now, not on first request
                default_fn(["warmup"])
                EmbeddingService._embed_func = default_fn
                logger.info("ChromaDB ONNX embedding function ready.")
            except Exception as e:
                logger.error(f"Failed to initialize embedding function: {e}")
                raise

        self.embed_func = EmbeddingService._embed_func

    def embed_text(self, text: str) -> List[float]:
        """Generate embedding vector for a single query/text."""
        if not text:
            return []
        res = self.embed_func([text])
        return list(res[0]) if res else []

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate embedding vectors for a batch of text chunks."""
        if not texts:
            return []
        return [list(v) for v in self.embed_func(texts)]
