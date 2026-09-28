import os
import uuid
from app.core.config import settings
from app.core.exceptions import AppException


def validate_file(filename: str, file_size: int) -> str:
    """Validate extension and size of uploaded file."""
    ext = os.path.splitext(filename)[1].lower()
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise AppException(
            code="UNSUPPORTED_FILE_TYPE",
            message=f"Unsupported file format '{ext}'. Allowed formats: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )
    
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if file_size > max_bytes:
        raise AppException(
            code="FILE_TOO_LARGE",
            message=f"File size exceeds maximum limit of {settings.MAX_UPLOAD_SIZE_MB}MB."
        )
    
    return ext


def generate_safe_filename(original_filename: str) -> str:
    """Generate safe filename with UUID prefix to prevent collisions/directory traversal."""
    ext = os.path.splitext(original_filename)[1].lower()
    unique_prefix = uuid.uuid4().hex[:12]
    clean_base = "".join(c for c in os.path.splitext(original_filename)[0] if c.isalnum() or c in ("-", "_")).rstrip()
    if not clean_base:
        clean_base = "file"
    return f"{unique_prefix}_{clean_base}{ext}"
