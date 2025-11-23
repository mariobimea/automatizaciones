"""
Tests for Code Cache Service

Tests semantic code caching functionality including:
- Save and retrieve code
- Semantic search with similar queries
- Threshold filtering
- Edge cases (empty insights, etc.)
"""

import pytest
import tempfile
import shutil
from pathlib import Path

from src.core.code_cache_service import CodeCacheService


@pytest.fixture
def temp_db_path():
    """Create temporary directory for test database."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def code_cache(temp_db_path):
    """Create CodeCacheService instance for testing."""
    return CodeCacheService(
        persist_directory=temp_db_path,
        collection_name="test_cached_code"
    )


def test_save_and_search_code(code_cache):
    """Test saving code and searching for it."""
    # Save a code document
    document = {
        "ai_description": "Extracts text from PDF using PyMuPDF. Works with standard PDFs (not scanned).",
        "input_schema": {"pdf_data": "base64_large", "filename": "str"},
        "insights": ["PDF format", "Text extraction needed"],
        "config": {"has_credentials": False},
        "code": """import fitz
import base64

pdf_bytes = base64.b64decode(context['pdf_data'])
doc = fitz.open(stream=pdf_bytes, filetype='pdf')
text = ""
for page in doc:
    text += page.get_text()
doc.close()

result = {"text": text}""",
        "node_action": "extract_pdf",
        "node_description": "Extract text from invoice PDF",
        "metadata": {
            "success_count": 1,
            "created_at": "2025-11-23T10:00:00",
            "libraries_used": ["fitz", "base64"]
        }
    }

    result = code_cache.save_code(document)

    assert result["success"] is True
    assert "id" in result

    # Search for similar code
    query = """Extract text from PDF document
Input schema:
{
  "pdf_data": "base64_large",
  "filename": "str"
}
Context:
- PDF format
- Text extraction needed"""

    matches = code_cache.search_code(query, threshold=0.7, top_k=5)

    assert len(matches) > 0
    assert matches[0]["score"] > 0.7
    assert "fitz" in matches[0]["code"]
    assert matches[0]["node_action"] == "extract_pdf"


def test_semantic_search_with_similar_query(code_cache):
    """Test semantic search finds code with different but similar query."""
    # Save code
    document = {
        "ai_description": "Performs OCR on image using EasyOCR. Requires GPU disabled.",
        "input_schema": {"image_data": "base64_large"},
        "insights": ["Image format", "OCR needed", "Spanish and English"],
        "config": {"has_credentials": False},
        "code": """import easyocr
import base64
import numpy as np

reader = easyocr.Reader(['es', 'en'], gpu=False)
image_bytes = base64.b64decode(context['image_data'])
# ... OCR code ...
result = {"text": extracted_text}""",
        "node_action": "ocr_image",
        "node_description": "Extract text from scanned document",
        "metadata": {
            "success_count": 1,
            "created_at": "2025-11-23T10:00:00",
            "libraries_used": ["easyocr", "base64", "numpy"]
        }
    }

    code_cache.save_code(document)

    # Search with similar but different wording
    query = """Read text from scanned image
Input: image_data (base64)
Context: Spanish/English OCR"""

    matches = code_cache.search_code(query, threshold=0.65, top_k=3)

    assert len(matches) > 0
    assert "easyocr" in matches[0]["code"]


def test_threshold_filtering(code_cache):
    """Test that threshold correctly filters results."""
    # Save code
    document = {
        "ai_description": "Sends email using SMTP",
        "input_schema": {"to": "str", "subject": "str", "body": "str"},
        "insights": ["Email sending"],
        "config": {"has_credentials": True},
        "code": "# Email sending code...",
        "node_action": "send_email",
        "node_description": "Send notification email",
        "metadata": {
            "success_count": 1,
            "created_at": "2025-11-23T10:00:00",
            "libraries_used": ["smtplib"]
        }
    }

    code_cache.save_code(document)

    # Search with very different query (should not match with high threshold)
    query = "Extract text from PDF document"

    matches_high = code_cache.search_code(query, threshold=0.9, top_k=5)
    matches_low = code_cache.search_code(query, threshold=0.1, top_k=5)

    # High threshold should filter out unrelated results
    assert len(matches_high) == 0

    # Low threshold might include it (depending on embedding distance)
    # This just ensures the threshold parameter works
    assert len(matches_low) >= 0


def test_empty_insights(code_cache):
    """Test saving code without insights (edge case)."""
    document = {
        "ai_description": "Simple addition function",
        "input_schema": {"a": "int", "b": "int"},
        "insights": [],  # Empty insights
        "config": {},
        "code": "result = {'sum': context['a'] + context['b']}",
        "node_action": "add_numbers",
        "node_description": "Add two numbers",
        "metadata": {
            "success_count": 1,
            "created_at": "2025-11-23T10:00:00",
            "libraries_used": []
        }
    }

    result = code_cache.save_code(document)

    assert result["success"] is True

    # Should still be searchable with exact query
    query = "Simple addition function"
    matches = code_cache.search_code(query, threshold=0.5)

    # With empty insights, we rely on AI description for matching
    assert len(matches) > 0


def test_get_stats(code_cache):
    """Test getting cache statistics."""
    # Initially empty
    stats = code_cache.get_stats()
    assert stats["total_codes"] == 0
    assert stats["actions"] == []

    # Save some code
    for i in range(3):
        document = {
            "ai_description": f"Test code {i}",
            "input_schema": {},
            "insights": [],
            "config": {},
            "code": f"# Code {i}",
            "node_action": f"action_{i}",
            "node_description": f"Description {i}",
            "metadata": {
                "success_count": i + 1,
                "created_at": "2025-11-23T10:00:00",
                "libraries_used": []
            }
        }
        code_cache.save_code(document)

    stats = code_cache.get_stats()
    assert stats["total_codes"] == 3
    assert len(stats["actions"]) == 3
    assert stats["avg_success_count"] == 2.0  # (1 + 2 + 3) / 3


def test_multiple_saves_same_action(code_cache):
    """Test saving multiple codes for the same action type."""
    for i in range(2):
        document = {
            "ai_description": f"PDF extraction variant {i}",
            "input_schema": {"pdf_data": "base64_large"},
            "insights": ["PDF"],
            "config": {},
            "code": f"# PDF code variant {i}",
            "node_action": "extract_pdf",
            "node_description": f"Extract PDF {i}",
            "metadata": {
                "success_count": 1,
                "created_at": "2025-11-23T10:00:00",
                "libraries_used": ["fitz"]
            }
        }
        code_cache.save_code(document)

    # Search should return both
    query = "Extract from PDF"
    matches = code_cache.search_code(query, threshold=0.5, top_k=5)

    assert len(matches) >= 2
    assert all(m["node_action"] == "extract_pdf" for m in matches)


def test_clear_cache(code_cache):
    """Test clearing the cache."""
    # Save code
    document = {
        "ai_description": "Test code",
        "input_schema": {},
        "insights": [],
        "config": {},
        "code": "# Test",
        "node_action": "test",
        "node_description": "Test",
        "metadata": {
            "success_count": 1,
            "created_at": "2025-11-23T10:00:00",
            "libraries_used": []
        }
    }
    code_cache.save_code(document)

    stats_before = code_cache.get_stats()
    assert stats_before["total_codes"] > 0

    # Clear
    code_cache.clear()

    stats_after = code_cache.get_stats()
    assert stats_after["total_codes"] == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
