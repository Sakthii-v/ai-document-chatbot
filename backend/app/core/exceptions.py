from fastapi import Request, status
from fastapi.responses import JSONResponse
from app.core.logging_config import logger


class AppException(Exception):
    def __init__(self, code: str, message: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class DocumentProcessingError(AppException):
    def __init__(self, message: str):
        super().__init__(code="DOCUMENT_PROCESSING_ERROR", message=message, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


class DuplicateDocumentError(AppException):
    def __init__(self, message: str):
        super().__init__(code="DUPLICATE_DOCUMENT", message=message, status_code=status.HTTP_409_CONFLICT)


class NotFoundError(AppException):
    def __init__(self, message: str):
        super().__init__(code="NOT_FOUND", message=message, status_code=status.HTTP_404_NOT_FOUND)


class OllamaUnavailableError(AppException):
    def __init__(self, message: str = "LLM service is currently unavailable."):
        super().__init__(code="OLLAMA_UNAVAILABLE", message=message, status_code=status.HTTP_503_SERVICE_UNAVAILABLE)


async def app_exception_handler(request: Request, exc: AppException):
    logger.error(f"AppException: code={exc.code}, message={exc.message}, path={request.url.path}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.code,
                "message": exc.message
            }
        }
    )


async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)} on path={request.url.path}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred. Please try again later."
            }
        }
    )
