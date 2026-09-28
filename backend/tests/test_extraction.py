import os
import tempfile
import pytest
from app.services.extraction_service import ExtractionService
from app.core.exceptions import DocumentProcessingError


def test_txt_extraction():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as f:
        f.write("Company Policy: Employees get 20 days annual leave.")
        temp_path = f.name

    try:
        extracted = ExtractionService.extract_txt(temp_path)
        assert len(extracted) == 1
        assert "20 days annual leave" in extracted[0]["text"]
        assert extracted[0]["page"] is None
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_empty_txt_raises_error():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as f:
        f.write("")
        temp_path = f.name

    try:
        with pytest.raises(DocumentProcessingError):
            ExtractionService.extract_txt(temp_path)
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
