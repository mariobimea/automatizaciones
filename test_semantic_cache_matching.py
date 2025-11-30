#!/usr/bin/env python3
"""
Test: ¿Por qué un mismo prompt no recupera código con el mismo prompt?

Este script:
1. Guarda un código en el semantic cache con un prompt específico
2. Busca usando el MISMO prompt y schema
3. Verifica si encuentra el código guardado
"""

import json
import sys
import os

# Add nova-rag to path
sys.path.insert(0, '/Users/marioferrer/automatizaciones/nova-rag/src')

from core.code_cache_service import CodeCacheService


def test_exact_match():
    """
    Test 1: Guardar y buscar con EXACTAMENTE el mismo prompt y schema
    """
    print("\n" + "="*80)
    print("TEST 1: Exact Match - Same prompt, same schema")
    print("="*80)

    # Initialize cache service
    cache = CodeCacheService(
        persist_directory="/tmp/test_semantic_cache",
        collection_name="test_exact_match"
    )

    # Clear cache
    cache.clear()
    print("✓ Cache cleared")

    # Define test data
    prompt = "Leer email y extraer PDF de facturas"
    input_schema = {
        "email_user": "str",
        "email_password": "str",
        "invoice_pdf": "base64_large"
    }

    code = """
import fitz
import base64

pdf_data = context['invoice_pdf']
pdf_bytes = base64.b64decode(pdf_data)

doc = fitz.open(stream=pdf_bytes, filetype="pdf")
text = doc[0].get_text()

result = {"extracted_text": text}
print(json.dumps({"status": "success", "context_updates": result}))
"""

    # Save code
    print(f"\n📝 Saving code...")
    print(f"   Prompt: {prompt}")
    print(f"   Schema: {json.dumps(input_schema, indent=2, sort_keys=True)}")

    result = cache.save_code({
        "ai_description": prompt,
        "input_schema": input_schema,
        "insights": [],
        "config": {"has_email_user": True, "has_email_password": True},
        "code": code,
        "node_action": "extract_pdf",
        "node_description": "Extract PDF text",
        "metadata": {
            "success_count": 1,
            "libraries_used": ["fitz", "base64"],
            "required_keys": ["invoice_pdf"]
        }
    })

    print(f"   Result: {result}")

    # Build EXACT SAME search query
    query_parts = []
    query_parts.append(f"Prompt: {prompt}")

    schema_str = json.dumps(input_schema, indent=2, sort_keys=True)
    query_parts.append(f"Input Schema:\n{schema_str}")

    query = "\n\n".join(query_parts)

    print(f"\n🔍 Searching with EXACT SAME query...")
    print(f"   Query:\n{query}")

    # Search with threshold 0.85
    matches = cache.search_code(
        query=query,
        threshold=0.85,
        top_k=5
    )

    print(f"\n📊 Results:")
    print(f"   Matches found: {len(matches)}")

    if matches:
        for i, match in enumerate(matches):
            print(f"\n   Match {i+1}:")
            print(f"      Score: {match['score']}")
            print(f"      Action: {match['node_action']}")
            print(f"      Code preview: {match['code'][:60]}...")
    else:
        print("\n   ❌ NO MATCHES FOUND!")

        # Try with threshold 0.0 to see ALL results
        print("\n   Trying with threshold=0.0 to see ALL results...")
        all_matches = cache.search_code(
            query=query,
            threshold=0.0,
            top_k=10
        )

        if all_matches:
            print(f"   Total codes in cache: {len(all_matches)}")
            for i, match in enumerate(all_matches):
                print(f"\n   Result {i+1}:")
                print(f"      Score: {match['score']}")
                print(f"      Action: {match['node_action']}")
        else:
            print("   ❌ NO RESULTS AT ALL (cache might be empty)")

    return len(matches) > 0


def test_slight_variation():
    """
    Test 2: Guardar con un prompt, buscar con pequeña variación
    """
    print("\n" + "="*80)
    print("TEST 2: Slight Variation - Similar prompt, same schema")
    print("="*80)

    cache = CodeCacheService(
        persist_directory="/tmp/test_semantic_cache",
        collection_name="test_variation"
    )

    cache.clear()
    print("✓ Cache cleared")

    # Save with one prompt
    prompt1 = "Leer email y extraer PDF de facturas"
    input_schema = {
        "email_user": "str",
        "email_password": "str",
        "invoice_pdf": "base64_large"
    }

    code = "import fitz\n# code here"

    print(f"\n📝 Saving code with prompt: '{prompt1}'")

    cache.save_code({
        "ai_description": prompt1,
        "input_schema": input_schema,
        "insights": [],
        "config": {},
        "code": code,
        "node_action": "extract_pdf",
        "node_description": "Extract PDF",
        "metadata": {"success_count": 1, "libraries_used": ["fitz"]}
    })

    # Search with similar prompt
    prompt2 = "Extraer PDF de facturas desde email"  # Different words, same idea

    query_parts = []
    query_parts.append(f"Prompt: {prompt2}")
    schema_str = json.dumps(input_schema, indent=2, sort_keys=True)
    query_parts.append(f"Input Schema:\n{schema_str}")
    query = "\n\n".join(query_parts)

    print(f"\n🔍 Searching with prompt: '{prompt2}'")

    matches = cache.search_code(query=query, threshold=0.85, top_k=5)

    print(f"\n📊 Results:")
    print(f"   Matches found: {len(matches)}")

    if matches:
        print(f"   ✅ FOUND! Score: {matches[0]['score']}")
    else:
        print(f"   ❌ NOT FOUND")

        # Check with lower threshold
        matches_low = cache.search_code(query=query, threshold=0.0, top_k=5)
        if matches_low:
            print(f"   Best score: {matches_low[0]['score']} (below threshold)")

    return len(matches) > 0


def test_schema_order():
    """
    Test 3: ¿El orden de las keys en el schema afecta?
    """
    print("\n" + "="*80)
    print("TEST 3: Schema Order - Same keys, different order")
    print("="*80)

    cache = CodeCacheService(
        persist_directory="/tmp/test_semantic_cache",
        collection_name="test_schema_order"
    )

    cache.clear()

    prompt = "Extract PDF"

    # Save with schema in one order
    schema1 = {
        "email_user": "str",
        "invoice_pdf": "base64_large",
        "email_password": "str"
    }

    print(f"\n📝 Saving with schema order: {list(schema1.keys())}")

    cache.save_code({
        "ai_description": prompt,
        "input_schema": schema1,
        "insights": [],
        "config": {},
        "code": "# code",
        "node_action": "extract",
        "node_description": "Extract",
        "metadata": {"success_count": 1, "libraries_used": []}
    })

    # Search with SAME KEYS but different order
    schema2 = {
        "invoice_pdf": "base64_large",
        "email_password": "str",
        "email_user": "str"
    }

    print(f"\n🔍 Searching with schema order: {list(schema2.keys())}")

    # Both functions use sort_keys=True, so order shouldn't matter
    query_parts = []
    query_parts.append(f"Prompt: {prompt}")
    schema_str = json.dumps(schema2, indent=2, sort_keys=True)
    query_parts.append(f"Input Schema:\n{schema_str}")
    query = "\n\n".join(query_parts)

    matches = cache.search_code(query=query, threshold=0.85, top_k=5)

    print(f"\n📊 Results:")
    print(f"   Matches found: {len(matches)}")

    if matches:
        print(f"   ✅ Order doesn't matter (score: {matches[0]['score']})")
    else:
        print(f"   ❌ Order MATTERS (unexpected!)")

    return len(matches) > 0


if __name__ == "__main__":
    print("\n🧪 SEMANTIC CACHE MATCHING TESTS")
    print("="*80)

    results = {
        "test1_exact_match": test_exact_match(),
        "test2_slight_variation": test_slight_variation(),
        "test3_schema_order": test_schema_order()
    }

    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)

    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")

    print("\n")

    # Exit with error if any test failed
    if not all(results.values()):
        sys.exit(1)
