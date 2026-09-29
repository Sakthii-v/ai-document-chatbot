from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging_config import setup_logging, logger
from app.core.exceptions import AppException, app_exception_handler, global_exception_handler
from app.db.init_db import init_db
from app.api.documents import router as documents_router
from app.api.chat import router as chat_router
from app.api.health import router as health_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup tasks
    setup_logging()
    logger.info("Initializing SQLite database tables...")
    init_db()
    logger.info("Application startup complete.")
    yield
    # Shutdown tasks
    logger.info("Application shutdown.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="ChatGPT-like RAG Document QA Chatbot built with Python, FastAPI, ChromaDB, Sentence Transformers, and Ollama.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS configuration for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",          # Local Vite dev server
        "http://localhost:4173",          # Local Vite preview
        "https://ai-document-chatbot-v5g1.onrender.com",  # Production frontend
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

# Include API routers under /api prefix
app.include_router(health_router, prefix=settings.API_V1_STR)
app.include_router(documents_router, prefix=settings.API_V1_STR)
app.include_router(chat_router, prefix=settings.API_V1_STR)


@app.get("/", summary="Root endpoint")
def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME} API!",
        "docs": "/docs",
        "health": f"{settings.API_V1_STR}/health"
    }
