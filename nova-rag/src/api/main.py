"""
NOVA RAG Microservice

FastAPI service for Retrieval-Augmented Generation (RAG).
Provides vector search over documentation for AI code generation.

Endpoints:
- POST /rag/query: Search documentation
- GET /rag/stats: Vector store statistics
- POST /rag/reload: Reload documentation (admin)
- GET /health: Health check
"""

import logging
import os
from contextlib import asynccontextmanager
from typing import Optional, Dict, List, Any

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field

# Import vector store (will be available after copying files)
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.vector_store import VectorStore
from core.document_loader import DocumentLoader

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global vector store instance
vector_store: Optional[VectorStore] = None
store_ready: bool = False


# === Request/Response Models ===

class QueryRequest(BaseModel):
    """Request model for RAG query."""
    query: str = Field(..., min_length=1, description="Search query")
    top_k: int = Field(5, ge=1, le=20, description="Number of results to return")
    filters: Optional[Dict[str, str]] = Field(None, description="Optional filters (source, topic)")


class QueryResult(BaseModel):
    """Single query result."""
    text: str
    source: str
    topic: str
    score: float = Field(0.0, description="Similarity score (0-1)")


class QueryResponse(BaseModel):
    """Response model for RAG query."""
    results: List[QueryResult]
    query: str
    count: int


class StatsResponse(BaseModel):
    """Response model for vector store stats."""
    total_documents: int
    sources: List[str]
    topics: List[str]
    status: str


class ReloadResponse(BaseModel):
    """Response model for reload request."""
    message: str
    documents_loaded: int


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str
    vector_store_ready: bool
    documents_loaded: int


# === Lifespan: Load vector store on startup ===

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load vector store on startup."""
    global vector_store, store_ready

    logger.info("=" * 60)
    logger.info("🚀 NOVA RAG Service Starting...")
    logger.info("=" * 60)

    try:
        # Initialize vector store
        logger.info("Initializing vector store...")
        vector_store = VectorStore()

        # Check if already loaded
        stats = vector_store.get_stats()
        if stats['total_documents'] > 0:
            logger.info(f"✓ Vector store already loaded with {stats['total_documents']} documents")
            store_ready = True
        else:
            # Load documentation
            logger.info("Loading documentation into vector store...")
            await load_documentation()
            logger.info("✓ Documentation loaded successfully")
            store_ready = True

        logger.info("=" * 60)
        logger.info("✅ RAG Service Ready!")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"❌ Failed to initialize RAG service: {e}")
        raise

    yield  # App runs

    # Shutdown
    logger.info("Shutting down RAG service...")


# === Helper Functions ===

async def load_documentation():
    """Load all documentation into vector store."""
    global vector_store

    if not vector_store:
        raise RuntimeError("Vector store not initialized")

    loader = DocumentLoader(chunk_size=700, chunk_overlap=100)
    all_chunks = []

    # Load integration docs
    logger.info("Loading integration docs...")
    integration_chunks = loader.load_integration_docs()
    all_chunks.extend(integration_chunks)
    logger.info(f"  ✓ Loaded {len(integration_chunks)} chunks from integrations")

    # Load PyMuPDF docs
    base_dir = Path(__file__).parent.parent.parent
    pymupdf_path = base_dir / "knowledge" / "official_docs" / "pymupdf_official.md"

    if pymupdf_path.exists():
        logger.info("Loading PyMuPDF documentation...")
        pymupdf_chunks = loader.load_markdown_file(
            file_path=str(pymupdf_path),
            source="pymupdf",
            topic="official"
        )
        all_chunks.extend(pymupdf_chunks)
        logger.info(f"  ✓ Loaded {len(pymupdf_chunks)} chunks from PyMuPDF")

    # Load EasyOCR docs
    easyocr_path = base_dir / "knowledge" / "official_docs" / "easyocr_official.md"

    if easyocr_path.exists():
        logger.info("Loading EasyOCR documentation...")
        easyocr_chunks = loader.load_markdown_file(
            file_path=str(easyocr_path),
            source="easyocr",
            topic="official"
        )
        all_chunks.extend(easyocr_chunks)
        logger.info(f"  ✓ Loaded {len(easyocr_chunks)} chunks from EasyOCR")

    # Add to vector store
    logger.info(f"Adding {len(all_chunks)} total chunks to vector store...")
    count = vector_store.add_documents(all_chunks)
    logger.info(f"  ✓ Successfully added {count} documents")

    return count


# === FastAPI App ===

app = FastAPI(
    title="NOVA RAG Service",
    description="Retrieval-Augmented Generation microservice for NOVA workflow engine",
    version="1.0.0",
    lifespan=lifespan
)


# === Endpoints ===

@app.get("/health", response_model=HealthResponse)
def health_check():
    """
    Health check endpoint.

    Returns service status and vector store readiness.
    """
    docs_count = 0
    if vector_store:
        stats = vector_store.get_stats()
        docs_count = stats['total_documents']

    return HealthResponse(
        status="healthy" if store_ready else "initializing",
        vector_store_ready=store_ready,
        documents_loaded=docs_count
    )


@app.post("/rag/query", response_model=QueryResponse)
def query_rag(request: QueryRequest):
    """
    Query the vector store for relevant documentation.

    Args:
        request: Query parameters (query, top_k, filters)

    Returns:
        List of relevant documentation chunks with similarity scores

    Example:
        POST /rag/query
        {
          "query": "how to extract text from PDF",
          "top_k": 5,
          "filters": {"source": "pymupdf"}
        }
    """
    if not store_ready or not vector_store:
        raise HTTPException(
            status_code=503,
            detail="Vector store not ready yet. Please wait a moment and retry."
        )

    try:
        # Query vector store
        # Extract filter_source and filter_topic from filters dict
        filter_source = None
        filter_topic = None
        if request.filters:
            filter_source = request.filters.get('source')
            filter_topic = request.filters.get('topic')

        results = vector_store.query(
            query_text=request.query,
            top_k=request.top_k,
            filter_source=filter_source,
            filter_topic=filter_topic
        )

        # Convert to response format
        # Convert distance to score: lower distance = higher score
        query_results = [
            QueryResult(
                text=doc['text'],
                source=doc['source'],
                topic=doc['topic'],
                score=1.0 - min(doc.get('distance', 0.0), 1.0)  # Normalize to 0-1
            )
            for doc in results
        ]

        return QueryResponse(
            results=query_results,
            query=request.query,
            count=len(query_results)
        )

    except Exception as e:
        logger.error(f"Error querying vector store: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/rag/stats", response_model=StatsResponse)
def get_stats():
    """
    Get vector store statistics.

    Returns:
        Total documents, sources, topics, and readiness status
    """
    if not vector_store:
        raise HTTPException(status_code=503, detail="Vector store not initialized")

    try:
        stats = vector_store.get_stats()

        return StatsResponse(
            total_documents=stats['total_documents'],
            sources=stats['sources'],
            topics=stats['topics'],
            status="ready" if store_ready else "loading"
        )

    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/rag/reload", response_model=ReloadResponse)
def reload_docs(background_tasks: BackgroundTasks):
    """
    Reload documentation into vector store.

    Admin endpoint to refresh documentation without redeploying.
    Runs in background to avoid blocking.

    Returns:
        Confirmation message with document count
    """
    if not store_ready or not vector_store:
        raise HTTPException(status_code=503, detail="Vector store not ready")

    try:
        # Clear existing docs
        logger.info("Clearing vector store...")
        vector_store.clear()

        # Reload in background
        background_tasks.add_task(load_documentation)

        return ReloadResponse(
            message="Documentation reload started in background",
            documents_loaded=0  # Will be updated after reload completes
        )

    except Exception as e:
        logger.error(f"Error reloading docs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
def root():
    """Root endpoint with service info."""
    return {
        "service": "NOVA RAG",
        "version": "1.0.0",
        "description": "Retrieval-Augmented Generation microservice",
        "endpoints": {
            "health": "GET /health",
            "query": "POST /rag/query",
            "stats": "GET /rag/stats",
            "reload": "POST /rag/reload"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
