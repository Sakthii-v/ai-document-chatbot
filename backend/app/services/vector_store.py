from typing import List, Dict, Any
import chromadb
from chromadb.config import Settings as ChromaSettings
from app.core.config import settings
from app.core.logging_config import logger


class VectorStore:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(VectorStore, cls).__new__(cls)
            logger.info(f"Initializing persistent ChromaDB client at {settings.CHROMA_PATH}")
            cls._instance.client = chromadb.PersistentClient(
                path=settings.CHROMA_PATH,
                settings=ChromaSettings(allow_reset=True, anonymized_telemetry=False)
            )
            cls._instance.collection = cls._instance.client.get_or_create_collection(
                name="document_chunks",
                metadata={"hnsw:space": "cosine"}
            )
            logger.info("ChromaDB collection 'document_chunks' ready.")
        return cls._instance

    def add_chunks(self, chunks: List[Dict[str, Any]], embeddings: List[List[float]]):
        """
        Store chunk text, embeddings, metadata, and IDs into ChromaDB.
        `chunks` item structure: {"id": str, "text": str, "metadata": dict}
        """
        if not chunks:
            return

        ids = [chunk["id"] for chunk in chunks]
        documents = [chunk["text"] for chunk in chunks]
        metadatas = [chunk["metadata"] for chunk in chunks]

        # Ensure page metadata is integer or string (ChromaDB requirement)
        for meta in metadatas:
            if meta.get("page") is None:
                meta["page"] = 1

        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )
        logger.info(f"Added {len(ids)} vector embeddings to ChromaDB.")

    def search(self, query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Perform similarity search using query embedding vector.
        Returns list of matched chunks with metadata and cosine similarity score.
        """
        if query_embedding is None or len(query_embedding) == 0:
            return []


        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )

        formatted_results = []
        if results and results.get("documents") and results["documents"][0]:
            docs = results["documents"][0]
            metas = results["metadatas"][0]
            distances = results["distances"][0]

            for doc, meta, dist in zip(docs, metas, distances):
                # Distance in cosine space: similarity = 1.0 - distance
                similarity = round(max(0.0, 1.0 - float(dist)), 4)
                formatted_results.append({
                    "text": doc,
                    "metadata": meta,
                    "similarity": similarity
                })

        logger.info(f"ChromaDB search retrieved {len(formatted_results)} results (top_k={top_k}).")
        return formatted_results

    def delete_document(self, document_id: int):
        """Delete all chunk vectors belonging to document_id."""
        try:
            self.collection.delete(where={"document_id": document_id})
            logger.info(f"Deleted vectors for document_id={document_id} from ChromaDB.")
        except Exception as e:
            logger.error(f"Failed to delete vectors for document_id={document_id}: {e}")

    def document_exists(self, document_id: int) -> bool:
        """Check if vectors exist for document_id."""
        try:
            res = self.collection.get(where={"document_id": document_id}, limit=1)
            return len(res.get("ids", [])) > 0
        except Exception:
            return False

    def is_healthy(self) -> bool:
        """Health check for ChromaDB."""
        try:
            self.collection.count()
            return True
        except Exception as e:
            logger.error(f"ChromaDB health check failed: {e}")
            return False
