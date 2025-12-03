"""
Code Cache Service - Semantic cache for AI-generated code.

Manages a ChromaDB collection for storing and retrieving previously
successful code executions based on semantic similarity.

Schema:
    - ai_description: Natural language description of what the code does
    - input_schema: Compact schema of input data structure
    - insights: List of context insights (from InputAnalyzer)
    - config: Configuration flags (credentials presence, etc.)
    - code: The actual Python code
    - node_action: Action type from workflow node
    - node_description: Description from workflow node
    - metadata: Success count, creation date, libraries used
"""

import logging
import os
from typing import List, Dict, Optional
from datetime import datetime

try:
    import chromadb
    from chromadb.config import Settings
    from openai import OpenAI
except ImportError:
    raise ImportError(
        "ChromaDB and OpenAI required. "
        "Install with: pip install chromadb openai"
    )

logger = logging.getLogger(__name__)


class CodeCacheService:
    """
    Manages semantic code cache using ChromaDB.

    Stores successful code executions with semantic search capabilities.
    Allows finding similar code based on task description and input schema.

    Example:
        >>> cache = CodeCacheService()
        >>>
        >>> # Save successful code
        >>> cache.save_code({
        ...     "ai_description": "Extracts text from PDF using PyMuPDF",
        ...     "input_schema": {"pdf_data": "base64_large"},
        ...     "insights": ["PDF format", "Text extraction needed"],
        ...     "code": "import fitz\\n...",
        ...     "node_action": "extract_pdf",
        ...     "node_description": "Extract text from invoice PDF"
        ... })
        >>>
        >>> # Search for similar code
        >>> matches = cache.search_code(
        ...     query="Extract text from PDF document",
        ...     threshold=0.85
        ... )
    """

    def __init__(
        self,
        persist_directory: Optional[str] = None,
        collection_name: str = "cached_code",
        client: Optional[chromadb.PersistentClient] = None
    ):
        """
        Initialize code cache service.

        Args:
            persist_directory: Where to store ChromaDB (defaults to /knowledge/vector_db)
            collection_name: Name of the collection (default: "cached_code")
            client: Optional existing ChromaDB client to reuse
        """
        from pathlib import Path
        import os

        # Default persist directory
        if persist_directory is None and client is None:
            base_dir = Path(__file__).parent.parent.parent.parent
            persist_directory = str(base_dir / "knowledge" / "vector_db")

        self.collection_name = collection_name

        # Initialize or reuse ChromaDB client
        if client:
            self.client = client
            logger.info(f"Reusing existing ChromaDB client for {collection_name}")
        else:
            os.makedirs(persist_directory, exist_ok=True)
            self.client = chromadb.PersistentClient(
                path=persist_directory,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            logger.info(f"Created new ChromaDB client at {persist_directory}")

        # Initialize OpenAI client for embeddings
        logger.info("Initializing OpenAI client for embeddings...")
        self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.embedding_model_name = "text-embedding-3-small"
        logger.info(f"Using OpenAI embedding model: {self.embedding_model_name}")

        # Get or create collection
        self.collection = self._initialize_collection()

    def _initialize_collection(self):
        """
        Initialize or get existing code cache collection.

        Returns:
            ChromaDB collection
        """
        try:
            collection = self.client.get_collection(name=self.collection_name)
            logger.info(f"Loaded existing collection: {self.collection_name}")
            logger.info(f"Collection size: {collection.count()} cached codes")
        except Exception:
            collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Semantic cache for AI-generated code"}
            )
            logger.info(f"Created new collection: {self.collection_name}")

        return collection

    def save_code(self, document: Dict) -> Dict[str, any]:
        """
        Save successful code execution to semantic cache.

        Args:
            document: Code cache document with fields:
                - ai_description (str): Natural language description
                - input_schema (dict): Compact input data schema
                - insights (list[str]): Context insights
                - config (dict): Configuration flags
                - code (str): The Python code
                - node_action (str): Action type
                - node_description (str): Node description
                - workflow_id (int, optional): Workflow ID for isolation
                - metadata (dict): success_count, created_at, libraries_used

        Returns:
            Dict with success status and document ID

        Example:
            >>> result = cache.save_code({
            ...     "ai_description": "Extracts text from PDF using PyMuPDF",
            ...     "input_schema": {"pdf_data": "base64_large"},
            ...     "insights": ["PDF format", "Text extraction"],
            ...     "config": {"has_credentials": False},
            ...     "code": "import fitz\\n...",
            ...     "node_action": "extract_pdf",
            ...     "node_description": "Extract invoice text",
            ...     "workflow_id": 5,
            ...     "metadata": {
            ...         "success_count": 1,
            ...         "created_at": "2025-11-23T10:00:00",
            ...         "libraries_used": ["fitz", "base64"]
            ...     }
            ... })
        """
        try:
            # Build searchable text for embedding
            searchable_text = self._build_searchable_text(document)

            # Generate embedding with OpenAI
            response = self.openai_client.embeddings.create(
                input=searchable_text,
                model=self.embedding_model_name
            )
            embedding = response.data[0].embedding

            # Generate unique ID
            doc_id = f"code_{self.collection.count()}_{datetime.now().timestamp()}"

            # Extract required keys from metadata (passed from executor)
            # These are the keys that the code ACTUALLY uses (extracted from code analysis)
            metadata_dict = document.get("metadata", {})
            required_keys = metadata_dict.get("required_keys", [])

            # Prepare metadata (flatten for ChromaDB)
            metadata = {
                "node_action": document.get("node_action", "unknown"),
                "node_description": document.get("node_description", ""),
                "success_count": metadata_dict.get("success_count", 1),
                "created_at": metadata_dict.get("created_at", datetime.now().isoformat()),
                "libraries_used": ",".join(metadata_dict.get("libraries_used", [])),
                # Store complex fields as JSON strings
                "input_schema": str(document.get("input_schema", {})),
                "insights": ",".join(document.get("insights", [])),
                "config": str(document.get("config", {})),
                # Store required keys for validation (not for semantic search)
                "required_keys": ",".join(required_keys) if required_keys else "",
                # Workflow isolation - cache is scoped per workflow
                "workflow_id": document.get("workflow_id") if document.get("workflow_id") is not None else -1
            }

            # Add to collection
            self.collection.add(
                ids=[doc_id],
                embeddings=[embedding],
                documents=[document["code"]],  # Store code as document
                metadatas=[metadata]
            )

            logger.info(f"✓ Saved code to cache: {doc_id} (action: {document.get('node_action')})")
            logger.debug(f"  AI description: {document.get('ai_description', '')[:80]}...")

            return {
                "success": True,
                "id": doc_id,
                "message": "Code saved to semantic cache"
            }

        except Exception as e:
            logger.error(f"Failed to save code to cache: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def search_code(
        self,
        query: str,
        threshold: float = 0.85,
        top_k: int = 5,
        available_keys: Optional[List[str]] = None,
        workflow_id: Optional[int] = None
    ) -> List[Dict]:
        """
        Search for similar code in semantic cache.

        Args:
            query: Search query (task description + input schema + insights)
            threshold: Minimum similarity score (0-1, default: 0.85)
            top_k: Maximum number of results (default: 5)
            available_keys: List of keys available in current context (for filtering)
            workflow_id: Workflow ID to filter results (only return code from same workflow)

        Returns:
            List of matching code documents with scores, sorted by similarity

        Example:
            >>> matches = cache.search_code(
            ...     query="Extract text from PDF\\nInput: pdf_data (base64)",
            ...     threshold=0.85,
            ...     top_k=3,
            ...     workflow_id=5
            ... )
            >>>
            >>> for match in matches:
            ...     print(f"Score: {match['score']}")
            ...     print(f"Code: {match['code'][:100]}...")
        """
        if self.collection.count() == 0:
            logger.debug("Code cache is empty, no results")
            return []

        try:
            # Generate query embedding with OpenAI
            response = self.openai_client.embeddings.create(
                input=query,
                model=self.embedding_model_name
            )
            query_embedding = response.data[0].embedding

            # Query collection (fetch more candidates if filtering by keys or workflow)
            fetch_count = top_k * 3 if (available_keys or workflow_id is not None) else top_k

            # Build where clause for workflow_id filtering
            where_clause = None
            if workflow_id is not None:
                where_clause = {"workflow_id": workflow_id}
                logger.debug(f"Filtering semantic cache by workflow_id={workflow_id}")

            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=fetch_count,
                include=['documents', 'metadatas', 'distances'],
                where=where_clause
            )

            # Format and filter results
            matches = []
            available_keys_set = set(available_keys) if available_keys else None

            for i in range(len(results['documents'][0])):
                distance = results['distances'][0][i]

                # Convert distance to score (0-1, higher is better)
                # ChromaDB uses L2 distance, normalize to 0-1 range
                score = 1.0 - min(distance / 2.0, 1.0)  # Heuristic normalization

                # Apply threshold filter
                if score < threshold:
                    continue

                metadata = results['metadatas'][0][i]

                # DON'T filter by required_keys here - let NOVA do the validation
                # This filter was too strict and rejected valid codes
                # Reason: required_keys extraction from code is not 100% accurate
                #         (e.g., dynamic keys, conditional access, etc.)
                # Let NOVA validate after retrieval with full context knowledge

                # Parse complex fields back from strings
                import ast
                try:
                    input_schema = ast.literal_eval(metadata.get("input_schema", "{}"))
                except:
                    input_schema = {}

                try:
                    config = ast.literal_eval(metadata.get("config", "{}"))
                except:
                    config = {}

                insights = metadata.get("insights", "").split(",") if metadata.get("insights") else []
                libraries = metadata.get("libraries_used", "").split(",") if metadata.get("libraries_used") else []
                required_keys = metadata.get("required_keys", "").split(",") if metadata.get("required_keys") else []

                matches.append({
                    "code": results['documents'][0][i],
                    "score": round(score, 4),
                    "node_action": metadata.get("node_action", "unknown"),
                    "node_description": metadata.get("node_description", ""),
                    "input_schema": input_schema,
                    "insights": insights,
                    "config": config,
                    "metadata": {
                        "success_count": metadata.get("success_count", 1),
                        "created_at": metadata.get("created_at", ""),
                        "libraries_used": libraries,
                        "required_keys": required_keys  # Return for validation
                    }
                })

                # Stop if we have enough matches
                if len(matches) >= top_k:
                    break

            logger.info(f"Found {len(matches)} compatible matches above threshold {threshold} (from {fetch_count} candidates)")

            return matches

        except Exception as e:
            logger.error(f"Error searching code cache: {e}")
            return []

    def _build_searchable_text(self, document: Dict) -> str:
        """
        Build searchable text from document for embedding.

        Simplified to use: Prompt + Full input schema (no insights).

        Args:
            document: Code cache document

        Returns:
            Searchable text string
        """
        import json

        parts = []

        # Prompt (main signal) - saved as-is from task
        if "ai_description" in document:
            parts.append(f"Prompt: {document['ai_description']}")

        # Full input schema (structure signal) - no filtering
        if "input_schema" in document:
            schema_text = json.dumps(document["input_schema"], indent=2, sort_keys=True)
            parts.append(f"Input Schema:\n{schema_text}")

        # Note: insights are no longer included in semantic search
        # They're saved for reference but don't affect similarity matching

        return "\n\n".join(parts)

    def get_stats(self) -> Dict:
        """
        Get code cache statistics.

        Returns:
            Dict with stats: total_codes, actions, avg_success_count
        """
        count = self.collection.count()

        if count == 0:
            return {
                "total_codes": 0,
                "actions": [],
                "avg_success_count": 0
            }

        # Get all metadata
        all_docs = self.collection.get(include=['metadatas'])

        actions = set()
        total_success = 0

        for metadata in all_docs['metadatas']:
            actions.add(metadata.get('node_action', 'unknown'))
            total_success += metadata.get('success_count', 1)

        return {
            "total_codes": count,
            "actions": sorted(list(actions)),
            "avg_success_count": round(total_success / count, 2) if count > 0 else 0
        }

    def clear(self):
        """
        Clear all cached code (destructive, cannot be undone).
        """
        logger.warning(f"Clearing code cache collection: {self.collection_name}")
        self.client.delete_collection(self.collection_name)
        self.collection = self._initialize_collection()
        logger.info("Code cache cleared and recreated")
