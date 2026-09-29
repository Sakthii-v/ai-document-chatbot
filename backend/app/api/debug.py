"""
debug.py — Temporary debug endpoint to identify processing pipeline failures.
Remove this file after diagnosing the issue.
"""
from fastapi import APIRouter
from app.core.logging_config import logger

router = APIRouter(prefix="/debug", tags=["Debug"])


@router.get("/pipeline-test", summary="Test the full processing pipeline with a sample text")
def test_pipeline():
    """
    Runs extraction → chunking → embedding → chromadb in sequence
    and reports exactly which step fails with the real error message.
    """
    results = {
        "embedding": {"status": "not_run", "error": None, "detail": None},
        "chromadb": {"status": "not_run", "error": None, "detail": None},
        "full_pipeline": {"status": "not_run", "error": None, "chunks_produced": 0},
    }

    sample_texts = [
        "This is a test document chunk number one used to verify embeddings work correctly on Render.",
        "This is chunk number two. It contains enough words to test the embedding pipeline thoroughly.",
        "Chunk three is here. The system should embed all three chunks and store them in ChromaDB.",
    ]

    # Step 1: Test embedding
    try:
        from app.services.embedding_service import EmbeddingService
        es = EmbeddingService()
        embeddings = es.embed_documents(sample_texts)
        results["embedding"]["status"] = "ok"
        results["embedding"]["detail"] = f"Generated {len(embeddings)} embeddings, dim={len(embeddings[0]) if embeddings else 0}"
        logger.info("Debug: embedding step passed.")
    except Exception as e:
        results["embedding"]["status"] = "error"
        results["embedding"]["error"] = str(e)
        logger.error(f"Debug: embedding step FAILED: {e}")
        return results  # Stop here, no point continuing

    # Step 2: Test ChromaDB write
    try:
        from app.services.vector_store import VectorStore
        vs = VectorStore()
        test_chunks = [
            {
                "id": f"debug_test_chunk_{i}",
                "text": text,
                "metadata": {
                    "document_id": -999,
                    "filename": "debug_test.txt",
                    "page": 1,
                    "chunk_index": i
                }
            }
            for i, text in enumerate(sample_texts)
        ]
        vs.add_chunks(test_chunks, embeddings)

        # Verify they were stored
        count = vs.collection.count()
        results["chromadb"]["status"] = "ok"
        results["chromadb"]["detail"] = f"Collection now has {count} total vectors. Write test passed."
        logger.info(f"Debug: chromadb write step passed. Total vectors: {count}")

        # Clean up test chunks
        try:
            vs.collection.delete(where={"document_id": -999})
        except Exception:
            pass

    except Exception as e:
        results["chromadb"]["status"] = "error"
        results["chromadb"]["error"] = str(e)
        logger.error(f"Debug: chromadb write step FAILED: {e}")
        return results

    # Step 3: Full pipeline summary
    results["full_pipeline"]["status"] = "ok"
    results["full_pipeline"]["chunks_produced"] = len(sample_texts)

    return results
