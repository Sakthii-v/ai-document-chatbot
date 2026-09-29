from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.database import get_db
from app.services.vector_store import VectorStore
from app.services.llm_service import LLMService

router = APIRouter(tags=["Health"])


@router.get("/health", summary="Check backend health and service statuses")
def get_health(db: Session = Depends(get_db)):
    # 1. Database check
    db_status = "ok"
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        db_status = "error"

    # 2. VectorStore check
    vector_store = VectorStore()
    chroma_status = "ok" if vector_store.is_healthy() else "error"

    # 3. Groq LLM check
    llm_service = LLMService()
    llm_ok = llm_service.check_health()
    llm_status = "ok" if llm_ok else "unavailable"

    overall_status = "healthy" if (db_status == "ok" and chroma_status == "ok" and llm_status == "ok") else "degraded"

    return {
        "status": overall_status,
        "services": {
            "database": db_status,
            "chromadb": chroma_status,
            "gemini": llm_status
        }
    }
