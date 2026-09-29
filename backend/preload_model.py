"""
preload_model.py — Run during Render build to pre-download the ONNX embedding model.

This prevents a slow cold-start on the first request by downloading and caching
the all-MiniLM-L6-v2 model (via chromadb's DefaultEmbeddingFunction) at build time.
"""
import sys

print("🔄 Pre-loading ChromaDB ONNX embedding model (all-MiniLM-L6-v2)...")

try:
    import chromadb.utils.embedding_functions as ef

    default_fn = ef.DefaultEmbeddingFunction()
    # Trigger actual model download by running a dummy embedding
    result = default_fn(["preload warmup"])
    print(f"✅ Embedding model loaded successfully. Output dim: {len(result[0])}")

except Exception as e:
    print(f"❌ Failed to preload embedding model: {e}", file=sys.stderr)
    # Don't fail the build — the model will be downloaded at runtime instead
    sys.exit(0)

print("✅ Model preload complete.")
