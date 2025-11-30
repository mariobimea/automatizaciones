#!/usr/bin/env python3
"""
Ver todos los códigos guardados en el semantic cache.
"""

import sys
import os

# Add nova-rag to path
sys.path.insert(0, '/Users/marioferrer/automatizaciones/nova-rag/src')

from core.code_cache_service import CodeCacheService


def view_all_cached_codes():
    """
    Mostrar todos los códigos guardados en el semantic cache.
    """
    print("\n" + "="*80)
    print("CÓDIGOS GUARDADOS EN SEMANTIC CACHE (ChromaDB)")
    print("="*80)

    # Connect to production cache
    # Path where Railway stores the cache
    cache_path = "/Users/marioferrer/automatizaciones/nova-rag/knowledge/vector_db"

    if not os.path.exists(cache_path):
        print(f"\n❌ Cache directory not found: {cache_path}")
        print("\nTrying alternative path (local)...")
        cache_path = "/tmp/nova_cache"

    print(f"\nCache path: {cache_path}")

    cache = CodeCacheService(
        persist_directory=cache_path,
        collection_name="cached_code"
    )

    # Get stats
    stats = cache.get_stats()

    print(f"\n📊 Cache Statistics:")
    print(f"   Total codes: {stats['total_codes']}")
    print(f"   Unique actions: {stats['actions']}")
    print(f"   Avg success count: {stats['avg_success_count']}")

    if stats['total_codes'] == 0:
        print("\n⚠️  Cache is empty!")
        return

    # Get all documents from ChromaDB
    print(f"\n{'='*80}")
    print("ALL CACHED CODES")
    print(f"{'='*80}")

    all_docs = cache.collection.get(include=['documents', 'metadatas'])

    for i, (doc_id, code, metadata) in enumerate(zip(
        all_docs['ids'],
        all_docs['documents'],
        all_docs['metadatas']
    ), 1):
        print(f"\n{'-'*80}")
        print(f"Code #{i}")
        print(f"{'-'*80}")
        print(f"ID: {doc_id}")
        print(f"Action: {metadata.get('node_action', 'unknown')}")
        print(f"Description: {metadata.get('node_description', 'N/A')}")
        print(f"Success count: {metadata.get('success_count', 0)}")
        print(f"Created: {metadata.get('created_at', 'N/A')}")

        # Parse complex fields
        import ast

        # Input schema
        try:
            input_schema = ast.literal_eval(metadata.get('input_schema', '{}'))
            print(f"\nInput Schema:")
            for key, type_val in input_schema.items():
                print(f"   {key}: {type_val}")
        except:
            print(f"\nInput Schema: {metadata.get('input_schema', 'N/A')}")

        # Config
        try:
            config = ast.literal_eval(metadata.get('config', '{}'))
            if config:
                print(f"\nConfig:")
                for key, val in config.items():
                    print(f"   {key}: {val}")
        except:
            pass

        # Libraries used
        libraries = metadata.get('libraries_used', '')
        if libraries:
            libs = libraries.split(',')
            print(f"\nLibraries: {', '.join(libs)}")

        # Required keys
        required_keys = metadata.get('required_keys', '')
        if required_keys:
            keys = required_keys.split(',')
            print(f"Required keys: {', '.join(keys)}")

        # Code
        print(f"\n📄 Code ({len(code)} chars):")
        print("-" * 80)
        print(code)
        print("-" * 80)


def search_example():
    """
    Ejemplo de búsqueda.
    """
    print("\n" + "="*80)
    print("EJEMPLO DE BÚSQUEDA")
    print("="*80)

    cache_path = "/Users/marioferrer/automatizaciones/nova-rag/knowledge/vector_db"

    cache = CodeCacheService(
        persist_directory=cache_path,
        collection_name="cached_code"
    )

    # Example search
    query = """Prompt: Extract the text from PDF

Input Schema:
{
  "email_metadata": "dict[4]",
  "has_pdf_decision": "str"
}"""

    print(f"\nSearching for:")
    print(query)
    print()

    matches = cache.search_code(
        query=query,
        threshold=0.0,  # Show all
        top_k=10
    )

    print(f"\nResults: {len(matches)}")

    for i, match in enumerate(matches, 1):
        print(f"\n{i}. Score: {match['score']:.3f}")
        print(f"   Action: {match['node_action']}")
        print(f"   Description: {match['node_description'][:60]}...")
        print(f"   Required keys: {match['metadata'].get('required_keys', [])}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='View semantic cache codes')
    parser.add_argument('--search', action='store_true', help='Run search example')
    parser.add_argument('--cache-path', type=str, help='Custom cache path')

    args = parser.parse_args()

    try:
        view_all_cached_codes()

        if args.search:
            search_example()

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
