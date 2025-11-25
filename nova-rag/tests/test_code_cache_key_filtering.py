"""
Tests for code cache key filtering.

Verifies that search_code filters results based on available_keys parameter.
"""

import pytest
from src.core.code_cache_service import CodeCacheService


@pytest.fixture
def code_cache():
    """Create fresh code cache for testing."""
    cache = CodeCacheService(persist_directory="./test_cache_keys")

    # Clear any existing data completely
    try:
        cache.client.delete_collection(name="cached_code")
        cache.collection = cache._initialize_collection()
    except:
        pass

    yield cache

    # Clean up after test
    try:
        cache.client.delete_collection(name="cached_code")
    except:
        pass


def test_filter_by_available_keys(code_cache):
    """Test that search filters codes by available keys."""

    # Save code 1: requires ["pdf_data", "client_id"]
    code_cache.save_code({
        "ai_description": "Extract text from PDF",
        "input_schema": {
            "pdf_data": "base64_large",
            "client_id": "int"
        },
        "insights": ["PDF format"],
        "config": {},
        "code": "pdf = context['pdf_data']\nclient = context['client_id']",
        "node_action": "extract_pdf",
        "node_description": "Extract PDF text",
        "metadata": {
            "success_count": 1,
            "created_at": "2025-11-25T10:00:00",
            "libraries_used": ["fitz"]
        }
    })

    # Save code 2: requires ["attachments", "client_id"]
    code_cache.save_code({
        "ai_description": "Extract text from attachment",
        "input_schema": {
            "attachments": "list[dict[2]]",
            "client_id": "int"
        },
        "insights": ["Multiple attachments"],
        "config": {},
        "code": "att = context['attachments']\nclient = context['client_id']",
        "node_action": "extract_attachment",
        "node_description": "Extract attachment text",
        "metadata": {
            "success_count": 1,
            "created_at": "2025-11-25T10:00:00",
            "libraries_used": ["email"]
        }
    })

    # Search WITH available_keys filter
    # We have: ["pdf_data", "client_id"]
    # Should ONLY match code 1 (not code 2 which requires "attachments")
    matches = code_cache.search_code(
        query="Extract text from document",
        threshold=0.5,
        top_k=5,
        available_keys=["pdf_data", "client_id"]
    )

    # Should only return code 1
    assert len(matches) == 1
    assert matches[0]['node_action'] == "extract_pdf"
    assert "pdf_data" in matches[0]['code']

    # Search WITHOUT available_keys filter
    # Should match BOTH codes (or at least more than with filter)
    matches_unfiltered = code_cache.search_code(
        query="Extract text from document",
        threshold=0.5,
        top_k=5,
        available_keys=None
    )

    # Without filter, should get at least as many results (possibly more)
    assert len(matches_unfiltered) >= len(matches)


def test_filter_rejects_code_with_missing_keys(code_cache):
    """Test that code requiring unavailable keys is rejected."""

    # Save code requiring 3 keys
    code_cache.save_code({
        "ai_description": "Process invoice with database",
        "input_schema": {
            "pdf_data": "base64_large",
            "db_host": "str",
            "db_password": "str"
        },
        "insights": ["Database access required"],
        "config": {"has_db_password": True},
        "code": "db = context['db_host']\npdf = context['pdf_data']",
        "node_action": "process_with_db",
        "node_description": "Process invoice with DB",
        "metadata": {
            "success_count": 1,
            "created_at": "2025-11-25T10:00:00",
            "libraries_used": ["psycopg2"]
        }
    })

    # Search with only 2 of the 3 required keys
    matches = code_cache.search_code(
        query="Process invoice",
        threshold=0.5,
        top_k=5,
        available_keys=["pdf_data", "client_id"]  # Missing db_host, db_password
    )

    # Should NOT match because we're missing keys
    assert len(matches) == 0


def test_filter_allows_code_with_subset_of_keys(code_cache):
    """Test that code requiring fewer keys is allowed."""

    # Save code requiring only 1 key
    code_cache.save_code({
        "ai_description": "Count items",
        "input_schema": {
            "items": "list[int]"
        },
        "insights": [],
        "config": {},
        "code": "count = len(context['items'])",
        "node_action": "count_items",
        "node_description": "Count number of items",
        "metadata": {
            "success_count": 1,
            "created_at": "2025-11-25T10:00:00",
            "libraries_used": []
        }
    })

    # Search with MORE keys than required
    matches = code_cache.search_code(
        query="Count items",
        threshold=0.5,
        top_k=5,
        available_keys=["items", "client_id", "invoice_number"]  # More than needed
    )

    # Should match because we have ALL required keys (and more)
    assert len(matches) == 1
    assert matches[0]['node_action'] == "count_items"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
