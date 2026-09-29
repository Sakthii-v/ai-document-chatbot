#!/usr/bin/env python3
"""
Pre-download the sentence-transformers model during Render build phase.
This avoids downloading at runtime which can cause health-check timeouts.
"""
import os
import sys

model_name = os.environ.get("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
print(f"[build] Pre-downloading embedding model: {model_name}", flush=True)

try:
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(model_name)
    print(f"[build] Model '{model_name}' downloaded and cached successfully.", flush=True)
except Exception as e:
    print(f"[build] WARNING: Could not pre-download model: {e}", flush=True)
    print("[build] App will fall back to ChromaDB default embedding function.", flush=True)
    sys.exit(0)  # Don't fail the build
