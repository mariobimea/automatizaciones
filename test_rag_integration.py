#!/usr/bin/env python3
"""
Test script for RAG Integration

Tests the complete flow:
1. Start nova-rag service locally
2. Query RAG service from nova-api (using RAGClient)
3. Verify responses and performance

Usage:
    # Terminal 1: Start RAG service
    cd nova-rag
    uvicorn src.api.main:app --port 8001

    # Terminal 2: Run this test
    python test_rag_integration.py
"""

import sys
import time
from pathlib import Path

# Add nova to path
sys.path.insert(0, str(Path(__file__).parent / "nova"))

from src.core.rag_client import RAGClient, RAGServiceError


def test_rag_health():
    """Test RAG service health check."""
    print("\n" + "=" * 60)
    print("TEST 1: RAG Service Health Check")
    print("=" * 60)

    client = RAGClient(base_url="http://localhost:8001")

    try:
        is_healthy = client.health_check()
        print(f"✅ Health check: {'HEALTHY' if is_healthy else 'NOT READY'}")

        if not is_healthy:
            print("⚠️  RAG service is not ready yet. Waiting 30s...")
            time.sleep(30)
            is_healthy = client.health_check()
            print(f"✅ Health check (retry): {'HEALTHY' if is_healthy else 'NOT READY'}")

        return is_healthy

    except Exception as e:
        print(f"❌ Health check failed: {e}")
        print("\n💡 Make sure nova-rag service is running:")
        print("   cd nova-rag && uvicorn src.api.main:app --port 8001")
        return False


def test_rag_stats():
    """Test RAG service statistics."""
    print("\n" + "=" * 60)
    print("TEST 2: RAG Service Statistics")
    print("=" * 60)

    client = RAGClient(base_url="http://localhost:8001")

    try:
        stats = client.get_stats()

        print(f"✅ Total documents: {stats['total_documents']}")
        print(f"✅ Sources: {', '.join(stats['sources'])}")
        print(f"✅ Topics: {', '.join(stats['topics'])}")
        print(f"✅ Status: {stats['status']}")

        return stats['total_documents'] > 0

    except Exception as e:
        print(f"❌ Stats query failed: {e}")
        return False


def test_rag_query():
    """Test RAG query functionality."""
    print("\n" + "=" * 60)
    print("TEST 3: RAG Query (PyMuPDF docs)")
    print("=" * 60)

    client = RAGClient(base_url="http://localhost:8001")

    test_query = "how to extract text from PDF"

    try:
        start_time = time.time()
        results = client.query(query=test_query, top_k=3)
        elapsed_ms = (time.time() - start_time) * 1000

        print(f"✅ Query: '{test_query}'")
        print(f"✅ Results: {len(results)} documents")
        print(f"✅ Latency: {elapsed_ms:.0f}ms")

        if results:
            print(f"\n📄 Top result:")
            top_result = results[0]
            print(f"   Source: {top_result['source']}")
            print(f"   Topic: {top_result['topic']}")
            print(f"   Score: {top_result.get('score', 'N/A')}")
            print(f"   Text preview: {top_result['text'][:200]}...")

        return len(results) > 0

    except Exception as e:
        print(f"❌ Query failed: {e}")
        return False


def test_rag_query_with_filters():
    """Test RAG query with filters."""
    print("\n" + "=" * 60)
    print("TEST 4: RAG Query with Filters (EasyOCR docs)")
    print("=" * 60)

    client = RAGClient(base_url="http://localhost:8001")

    test_query = "how to use OCR"

    try:
        start_time = time.time()
        results = client.query(
            query=test_query,
            top_k=3,
            filters={"source": "easyocr"}
        )
        elapsed_ms = (time.time() - start_time) * 1000

        print(f"✅ Query: '{test_query}'")
        print(f"✅ Filter: source='easyocr'")
        print(f"✅ Results: {len(results)} documents")
        print(f"✅ Latency: {elapsed_ms:.0f}ms")

        # Verify all results are from easyocr
        all_easyocr = all(r['source'] == 'easyocr' for r in results)
        print(f"✅ All results from EasyOCR: {all_easyocr}")

        return len(results) > 0 and all_easyocr

    except Exception as e:
        print(f"❌ Query with filters failed: {e}")
        return False


def test_knowledge_manager_integration():
    """Test KnowledgeManager using RAG client."""
    print("\n" + "=" * 60)
    print("TEST 5: KnowledgeManager Integration")
    print("=" * 60)

    try:
        from src.core.ai.knowledge_manager import KnowledgeManager

        # Initialize with RAG client
        manager = KnowledgeManager(use_vector_store=True)

        # Test detect integrations
        task = "Extract text from a PDF invoice"
        context = {"pdf_data": "base64...", "recommended_extraction_method": "pymupdf"}

        integrations = manager.detect_integrations(task, context)
        print(f"✅ Detected integrations: {integrations}")

        # Test retrieve docs
        docs = manager.retrieve_docs(task=task, integrations=["pymupdf"], top_k_per_integration=2)
        print(f"✅ Retrieved docs: {len(docs)} chars")
        print(f"   Preview: {docs[:200]}...")

        # Test build prompt
        prompt, metadata = manager.build_prompt(task=task, context=context)
        print(f"✅ Built prompt: {len(prompt)} chars")
        print(f"   Integrations detected: {metadata['integrations_detected']}")
        print(f"   Retrieval method: {metadata['retrieval_method']}")
        print(f"   Docs retrieved: {metadata['docs_retrieved_count']}")

        return True

    except Exception as e:
        print(f"❌ KnowledgeManager integration failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("🧪 NOVA RAG Integration Tests")
    print("=" * 60)

    results = {
        "health_check": False,
        "stats": False,
        "query": False,
        "query_with_filters": False,
        "knowledge_manager": False
    }

    # Run tests
    results["health_check"] = test_rag_health()

    if results["health_check"]:
        results["stats"] = test_rag_stats()
        results["query"] = test_rag_query()
        results["query_with_filters"] = test_rag_query_with_filters()
        results["knowledge_manager"] = test_knowledge_manager_integration()
    else:
        print("\n⚠️  Skipping remaining tests (RAG service not healthy)")

    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)

    passed = sum(results.values())
    total = len(results)

    for test_name, passed_test in results.items():
        status = "✅ PASS" if passed_test else "❌ FAIL"
        print(f"{status} - {test_name}")

    print(f"\n🎯 Total: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! RAG integration is working correctly.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
