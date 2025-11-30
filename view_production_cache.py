#!/usr/bin/env python3
"""
Ver códigos guardados en el semantic cache de PRODUCCIÓN vía API.
"""

import requests
import json


def get_cache_stats():
    """
    Get cache stats from production nova-rag service.
    """
    url = "https://automatizaciones-production-92f8.up.railway.app/code/stats"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error getting stats: {e}")
        return None


def search_all_codes():
    """
    Search with a very generic query to get all codes.
    """
    url = "https://automatizaciones-production-92f8.up.railway.app/code/search"

    # Generic query that should match anything
    payload = {
        "query": "code",  # Very generic
        "threshold": 0.0,  # Get ALL codes
        "top_k": 100  # Up to 100 codes
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error searching: {e}")
        return None


if __name__ == "__main__":
    print("\n" + "="*80)
    print("SEMANTIC CACHE - PRODUCTION (nova-rag)")
    print("="*80)

    # Get stats
    print("\n📊 Cache Statistics:")
    stats = get_cache_stats()

    if stats:
        print(f"   Status: {stats.get('status', 'unknown')}")
        print(f"   Message: {stats.get('message', 'N/A')}")
    else:
        print("   ❌ Could not get stats")

    # Search for all codes
    print(f"\n{'='*80}")
    print("SEARCHING ALL CACHED CODES")
    print(f"{'='*80}")

    result = search_all_codes()

    if not result:
        print("\n❌ Could not search codes")
        exit(1)

    matches = result.get('matches', [])
    count = result.get('count', 0)

    print(f"\nTotal codes found: {count}")

    if count == 0:
        print("\n⚠️  No codes in cache!")
        print("\nPossible reasons:")
        print("1. Cache was never populated (no successful executions saved)")
        print("2. Cache was cleared")
        print("3. nova-rag service restarted and lost in-memory cache")
        exit(0)

    # Show all codes
    print(f"\n{'='*80}")
    print("ALL CACHED CODES")
    print(f"{'='*80}")

    for i, match in enumerate(matches, 1):
        print(f"\n{'-'*80}")
        print(f"Code #{i}")
        print(f"{'-'*80}")
        print(f"Score: {match.get('score', 0):.3f}")
        print(f"Action: {match.get('node_action', 'unknown')}")
        print(f"Description: {match.get('node_description', 'N/A')}")

        # Input schema
        input_schema = match.get('input_schema', {})
        if input_schema:
            print(f"\nInput Schema:")
            for key, type_val in input_schema.items():
                print(f"   {key}: {type_val}")

        # Config
        config = match.get('config', {})
        if config:
            print(f"\nConfig:")
            for key, val in config.items():
                print(f"   {key}: {val}")

        # Metadata
        metadata = match.get('metadata', {})
        if metadata:
            print(f"\nMetadata:")
            print(f"   Success count: {metadata.get('success_count', 0)}")
            print(f"   Created: {metadata.get('created_at', 'N/A')}")

            libraries = metadata.get('libraries_used', [])
            if libraries:
                print(f"   Libraries: {', '.join(libraries)}")

            required_keys = metadata.get('required_keys', [])
            if required_keys:
                print(f"   Required keys: {', '.join(required_keys)}")

        # Code
        code = match.get('code', '')
        print(f"\n📄 Code ({len(code)} chars):")
        print("-" * 80)
        print(code)
        print("-" * 80)

    print(f"\n{'='*80}")
    print(f"Total: {count} codes in semantic cache")
    print(f"{'='*80}\n")
