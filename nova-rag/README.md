# NOVA RAG Microservice

Retrieval-Augmented Generation (RAG) microservice for NOVA workflow engine.

Provides vector search over documentation to support AI code generation.

## Architecture

```
┌─────────────────────────────────────────┐
│         NOVA RAG Service                │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │  FastAPI App                     │  │
│  │  - POST /rag/query               │  │
│  │  - GET  /rag/stats               │  │
│  │  - POST /rag/reload              │  │
│  │  - GET  /health                  │  │
│  └──────────────────────────────────┘  │
│               │                         │
│               ▼                         │
│  ┌──────────────────────────────────┐  │
│  │  ChromaDB Vector Store           │  │
│  │  - Sentence Transformers         │  │
│  │  - Documentation chunks          │  │
│  │  - Semantic search               │  │
│  └──────────────────────────────────┘  │
│               │                         │
│               ▼                         │
│  ┌──────────────────────────────────┐  │
│  │  Knowledge Base                  │  │
│  │  - PyMuPDF docs                  │  │
│  │  - EasyOCR docs                  │  │
│  │  - Integration examples          │  │
│  └──────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

## API Endpoints

### Query Documentation

```bash
POST /rag/query
{
  "query": "how to extract text from PDF",
  "top_k": 5,
  "filters": {
    "source": "pymupdf",
    "topic": "official"
  }
}
```

Response:
```json
{
  "results": [
    {
      "text": "To extract text from a PDF...",
      "source": "pymupdf",
      "topic": "official",
      "score": 0.92
    }
  ],
  "query": "how to extract text from PDF",
  "count": 5
}
```

### Get Statistics

```bash
GET /rag/stats
```

Response:
```json
{
  "total_documents": 1234,
  "sources": ["pymupdf", "easyocr", "requests"],
  "topics": ["official", "tutorial"],
  "status": "ready"
}
```

### Health Check

```bash
GET /health
```

Response:
```json
{
  "status": "healthy",
  "vector_store_ready": true,
  "documents_loaded": 1234
}
```

### Reload Documentation

```bash
POST /rag/reload
```

Admin endpoint to refresh documentation without redeploying.

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run service
uvicorn src.api.main:app --reload --port 8001

# Test endpoint
curl http://localhost:8001/health
```

## Railway Deployment

This service deploys as a separate Railway service from the main NOVA API.

### Environment Variables

No required environment variables. Optional:

- `CHROMA_DB_PATH`: Custom path for vector store (default: `/tmp/chroma_db`)

### Deployment

```bash
# Deploy from nova-rag directory
railway up
```

The service will:
1. Install dependencies (chromadb, sentence-transformers)
2. Start FastAPI app
3. Load documentation into vector store on first startup
4. Serve RAG query endpoints

## Integration with NOVA

NOVA API/Workers communicate with this service via HTTP:

```python
# In nova/src/core/rag_client.py
import requests

class RAGClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def query(self, query: str, top_k: int = 5):
        response = requests.post(
            f"{self.base_url}/rag/query",
            json={"query": query, "top_k": top_k}
        )
        return response.json()
```

## Performance

- **Startup**: ~30-60 seconds (loads sentence-transformers model)
- **Query latency**: ~100-300ms per query
- **Memory**: ~1GB (model + vector store)
- **Cost**: ~$5-7/month on Railway (single service)

## Tech Stack

- **FastAPI**: Web framework
- **ChromaDB**: Vector database
- **Sentence Transformers**: Embedding model (all-MiniLM-L6-v2)
- **Python 3.11**: Runtime
