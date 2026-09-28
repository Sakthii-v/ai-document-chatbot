from typing import List
import chromadb.utils.embedding_functions as ef
from sentence_transformers import SentenceTransformer
from app.core.config import settings
from app.core.logging_config import logger


class EmbeddingService:
    _instance = None
    _embed_func = None
    _is_chroma_default = False

    def __init__(self):
        if EmbeddingService._embed_func is None:
            model_name = settings.EMBEDDING_MODEL
            logger.info(f"Initializing embedding service with model '{model_name}'...")
            try:
                # Try loading SentenceTransformer first
                model = SentenceTransformer(model_name)
                EmbeddingService._embed_func = lambda texts: model.encode(texts, convert_to_numpy=True).tolist()
                logger.info("SentenceTransformer initialized successfully.")
            except Exception as e:
                logger.warning(f"SentenceTransformer load failed ({e}), using ChromaDB ONNX DefaultEmbeddingFunction...")
                default_fn = ef.DefaultEmbeddingFunction()
                EmbeddingService._embed_func = lambda texts: default_fn(texts)
                EmbeddingService._is_chroma_default = True
                logger.info("ChromaDB ONNX DefaultEmbeddingFunction initialized successfully.")

        self.embed_func = EmbeddingService._embed_func

    def embed_text(self, text: str) -> List[float]:
        """Generate embedding vector for a single query/text."""
        if not text:
            return []
        res = self.embed_func([text])
        return res[0] if res else []

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate embedding vectors for a batch of text chunks."""
        if not texts:
            return []
        return self.embed_func(texts)
