"""
Code Cache API Routes

Endpoints for semantic code cache:
- POST /code/search: Search for similar cached code
- POST /code/save: Save successful code execution
- GET /code/stats: Get cache statistics
"""

import logging
from typing import List, Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# Router
router = APIRouter(prefix="/code", tags=["code_cache"])


# === Request/Response Models ===

class CodeSearchRequest(BaseModel):
    """Request model for code search."""
    query: str = Field(..., min_length=1, description="Search query (task + schema + insights)")
    threshold: float = Field(0.85, ge=0.0, le=1.0, description="Minimum similarity score")
    top_k: int = Field(5, ge=1, le=20, description="Maximum results to return")
    available_keys: Optional[List[str]] = Field(None, description="Keys available in current context (for filtering)")


class CodeMatch(BaseModel):
    """Single code match result."""
    code: str = Field(..., description="The Python code")
    score: float = Field(..., description="Similarity score (0-1)")
    node_action: str = Field(..., description="Node action type")
    node_description: str = Field(..., description="Node description")
    input_schema: Dict = Field(..., description="Input data schema")
    insights: List[str] = Field(..., description="Context insights")
    config: Dict = Field(..., description="Configuration flags")
    metadata: Dict = Field(..., description="Metadata (success_count, created_at, libraries)")


class CodeSearchResponse(BaseModel):
    """Response model for code search."""
    matches: List[CodeMatch]
    query: str
    count: int
    threshold: float


class CodeSaveRequest(BaseModel):
    """Request model for saving code."""
    ai_description: str = Field(..., description="Natural language description of what code does")
    input_schema: Dict = Field(..., description="Compact input data schema")
    insights: List[str] = Field(default=[], description="Context insights from InputAnalyzer")
    config: Dict = Field(default={}, description="Configuration flags (credentials, etc.)")
    code: str = Field(..., min_length=1, description="The Python code")
    node_action: str = Field(..., description="Action type from workflow node")
    node_description: str = Field(..., description="Description from workflow node")
    metadata: Dict = Field(
        ...,
        description="Metadata: success_count, created_at, libraries_used"
    )


class CodeSaveResponse(BaseModel):
    """Response model for code save."""
    success: bool
    id: Optional[str] = None
    message: str
    error: Optional[str] = None


class CodeStatsResponse(BaseModel):
    """Response model for cache statistics."""
    total_codes: int
    actions: List[str]
    avg_success_count: float


# === Endpoints ===

@router.post("/search", response_model=CodeSearchResponse)
def search_code(request: CodeSearchRequest):
    """
    Search for similar cached code based on semantic similarity.

    The query should combine:
    - Task description
    - Input schema (compact format)
    - Context insights

    Returns cached code that matches the query above the threshold.

    Example:
        POST /code/search
        {
          "query": "Extract text from PDF\\nInput: pdf_data (base64_large)\\nContext: PDF format",
          "threshold": 0.85,
          "top_k": 5
        }
    """
    # Import from main to access global instance
    from ..main import code_cache_service

    if not code_cache_service:
        raise HTTPException(
            status_code=503,
            detail="Code cache service not initialized"
        )

    try:
        # Search cache
        matches = code_cache_service.search_code(
            query=request.query,
            threshold=request.threshold,
            top_k=request.top_k,
            available_keys=request.available_keys
        )

        # Convert to response format
        code_matches = [
            CodeMatch(**match) for match in matches
        ]

        return CodeSearchResponse(
            matches=code_matches,
            query=request.query,
            count=len(code_matches),
            threshold=request.threshold
        )

    except Exception as e:
        logger.error(f"Error searching code cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/save", response_model=CodeSaveResponse)
def save_code(request: CodeSaveRequest):
    """
    Save successful code execution to semantic cache.

    Stores the code with its description, input schema, insights,
    and metadata for future semantic retrieval.

    Example:
        POST /code/save
        {
          "ai_description": "Extracts text from PDF using PyMuPDF. Works with standard PDFs.",
          "input_schema": {"pdf_data": "base64_large"},
          "insights": ["PDF format", "Text extraction needed"],
          "config": {"has_credentials": false},
          "code": "import fitz\\nimport base64\\n...",
          "node_action": "extract_pdf",
          "node_description": "Extract text from invoice PDF",
          "metadata": {
            "success_count": 1,
            "created_at": "2025-11-23T10:00:00",
            "libraries_used": ["fitz", "base64"]
          }
        }
    """
    # Import from main to access global instance
    from ..main import code_cache_service

    if not code_cache_service:
        raise HTTPException(
            status_code=503,
            detail="Code cache service not initialized"
        )

    try:
        # Build document
        document = {
            "ai_description": request.ai_description,
            "input_schema": request.input_schema,
            "insights": request.insights,
            "config": request.config,
            "code": request.code,
            "node_action": request.node_action,
            "node_description": request.node_description,
            "metadata": request.metadata
        }

        # Save to cache
        result = code_cache_service.save_code(document)

        return CodeSaveResponse(**result)

    except Exception as e:
        logger.error(f"Error saving code to cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats", response_model=CodeStatsResponse)
def get_code_stats():
    """
    Get code cache statistics.

    Returns:
        - total_codes: Number of cached code snippets
        - actions: List of unique action types
        - avg_success_count: Average success count per code
    """
    # Import from main to access global instance
    from ..main import code_cache_service

    if not code_cache_service:
        raise HTTPException(
            status_code=503,
            detail="Code cache service not initialized"
        )

    try:
        stats = code_cache_service.get_stats()
        return CodeStatsResponse(**stats)

    except Exception as e:
        logger.error(f"Error getting code cache stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/clear")
def clear_code_cache():
    """
    Clear all codes from semantic cache (admin operation).

    WARNING: This is destructive and cannot be undone.
    All cached code will be deleted.

    Returns:
        Confirmation message with count of deleted codes
    """
    # Import from main to access global instance
    from ..main import code_cache_service

    if not code_cache_service:
        raise HTTPException(
            status_code=503,
            detail="Code cache service not initialized"
        )

    try:
        # Get count before clearing
        stats = code_cache_service.get_stats()
        count_before = stats['total_codes']

        # Clear cache
        code_cache_service.clear()

        logger.warning(f"Code cache cleared: {count_before} codes deleted")

        return {
            "success": True,
            "message": f"Code cache cleared successfully",
            "codes_deleted": count_before
        }

    except Exception as e:
        logger.error(f"Error clearing code cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))
