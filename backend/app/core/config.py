import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Document Chatbot"
    API_V1_STR: str = "/api"

    # Google Gemini API settings (free tier — https://aistudio.google.com/app/apikey)
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-flash"

    # Database settings
    DATABASE_URL: str = "sqlite:///./app.db"

    # ChromaDB settings
    CHROMA_PATH: str = "./chroma_data"

    # Upload settings
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE_MB: int = 25  # 25 MB max file size
    ALLOWED_EXTENSIONS: set[str] = {".pdf", ".docx", ".txt"}

    # RAG & Embedding settings
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    TOP_K: int = 5

    CHUNK_SIZE: int = 700
    CHUNK_OVERLAP: int = 120

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")



settings = Settings()

# Ensure directories exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.CHROMA_PATH, exist_ok=True)
