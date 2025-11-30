#!/usr/bin/env python3
"""
Analizar exactamente qué input_schemas se guardaron vs se están buscando.
"""

import requests
import json
import psycopg2
from psycopg2.extras import RealDictCursor


def connect_db():
    """Connect to production database"""
    return psycopg2.connect(
        "postgresql://postgres:KEeNOLKQWzndcAzbXAMAXzxJJrhGmPbM@trolley.proxy.rlwy.net:23108/railway"
    )


def get_cached_schemas():
    """
    Get all input_schemas from semantic cache (production).
    """
    url = "https://automatizaciones-production-92f8.up.railway.app/code/search"

    payload = {
        "query": "Extract text from PDF",
        "threshold": 0.0,  # Get ALL
        "top_k": 20
    }

    response = requests.post(url, json=payload, timeout=10)
    response.raise_for_status()

    result = response.json()
    matches = result.get('matches', [])

    cached_schemas = []
    for match in matches:
        cached_schemas.append({
            'node_action': match['node_action'],
            'node_description': match['node_description'],
            'input_schema': match['input_schema'],
            'score': match['score']
        })

    return cached_schemas


def get_search_queries():
    """
    Get search queries from Chain of Work (ai_metadata.semantic_cache_search).
    """
    conn = connect_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    query = """
    SELECT
        cw.id,
        cw.node_id,
        cw.ai_metadata,
        cw.timestamp
    FROM chain_of_work cw
    WHERE cw.node_type = 'action'
      AND cw.status = 'success'
      AND cw.ai_metadata::text LIKE '%semantic_cache_search%'
    ORDER BY cw.timestamp DESC
    LIMIT 10
    """

    cur.execute(query)
    rows = cur.fetchall()

    search_queries = []
    for row in rows:
        ai_metadata = row['ai_metadata']
        if isinstance(ai_metadata, str):
            ai_metadata = json.loads(ai_metadata)

        semantic_search = ai_metadata.get('semantic_cache_search', {})

        if semantic_search:
            # Extract schema from query
            query_text = semantic_search.get('query', '')

            # Parse input_schema from query
            # Query format: "Prompt: ...\n\nInput Schema:\n{...}"
            schema_str = None
            if 'Input Schema:' in query_text:
                parts = query_text.split('Input Schema:')
                if len(parts) > 1:
                    schema_str = parts[1].strip()
                    try:
                        schema_dict = json.loads(schema_str)
                    except:
                        schema_dict = None

            search_queries.append({
                'node_id': row['node_id'],
                'timestamp': row['timestamp'],
                'query': query_text[:200] + '...' if len(query_text) > 200 else query_text,
                'input_schema': schema_dict if schema_str else {},
                'available_keys': semantic_search.get('available_keys', []),
                'all_available_keys': semantic_search.get('all_available_keys', []),
                'results_count': len(semantic_search.get('results_above_threshold', [])),
                'all_results': semantic_search.get('all_results', [])
            })

    cur.close()
    conn.close()

    return search_queries


def compare_schemas():
    """
    Compare schemas: what's cached vs what's being searched.
    """
    print("\n" + "="*80)
    print("ANÁLISIS: INPUT SCHEMAS GUARDADOS VS BUSCADOS")
    print("="*80)

    # Get cached schemas
    print("\n📦 Getting cached schemas from semantic cache...")
    cached = get_cached_schemas()

    print(f"\n✓ Found {len(cached)} cached codes")

    # Get search queries
    print("\n🔍 Getting search queries from Chain of Work...")
    searches = get_search_queries()

    print(f"✓ Found {len(searches)} search queries")

    # Display cached schemas
    print("\n" + "="*80)
    print("1️⃣  INPUT SCHEMAS GUARDADOS EN CACHE")
    print("="*80)

    for i, item in enumerate(cached, 1):
        print(f"\n{'-'*80}")
        print(f"Cached Code #{i}")
        print(f"{'-'*80}")
        print(f"Node Action: {item['node_action']}")
        print(f"Description: {item['node_description']}")
        print(f"\nInput Schema (guardado):")
        print(json.dumps(item['input_schema'], indent=2, sort_keys=True))
        print(f"\nScore (from last search): {item['score']:.3f}")

    # Display search queries
    print("\n" + "="*80)
    print("2️⃣  INPUT SCHEMAS BUSCADOS (queries)")
    print("="*80)

    for i, search in enumerate(searches, 1):
        print(f"\n{'-'*80}")
        print(f"Search Query #{i}")
        print(f"{'-'*80}")
        print(f"Node ID: {search['node_id']}")
        print(f"Timestamp: {search['timestamp']}")
        print(f"\nQuery (first 200 chars):")
        print(search['query'])
        print(f"\nInput Schema (buscado):")
        print(json.dumps(search['input_schema'], indent=2, sort_keys=True))
        print(f"\nAvailable keys: {search['available_keys']}")
        print(f"All available keys: {search['all_available_keys']}")
        print(f"\nResults above threshold (0.85): {search['results_count']}")

        # Show all results with scores
        all_results = search['all_results']
        if all_results:
            print(f"\nAll results (threshold 0.0):")
            for j, result in enumerate(all_results[:5], 1):  # Show top 5
                print(f"  {j}. {result['node_action']:30s} score={result['score']:.3f} above_threshold={result.get('above_threshold', False)}")
                print(f"     Schema: {result.get('input_schema', {})}")

    # Comparison analysis
    print("\n" + "="*80)
    print("3️⃣  ANÁLISIS DE DIFERENCIAS")
    print("="*80)

    if cached and searches:
        # Compare first cached schema with first search
        cached_schema = cached[0]['input_schema']
        search_schema = searches[0]['input_schema']

        print(f"\nComparando:")
        print(f"  Cached: {cached[0]['node_action']}")
        print(f"  Search: {searches[0]['node_id']}")

        # Keys in cached but not in search
        cached_keys = set(cached_schema.keys())
        search_keys = set(search_schema.keys())

        only_cached = cached_keys - search_keys
        only_search = search_keys - cached_keys
        common = cached_keys & search_keys

        print(f"\n📊 Key analysis:")
        print(f"  Common keys: {len(common)} → {sorted(common)}")
        print(f"  Only in cached: {len(only_cached)} → {sorted(only_cached)}")
        print(f"  Only in search: {len(only_search)} → {sorted(only_search)}")

        # Type differences for common keys
        if common:
            print(f"\n🔍 Type comparison for common keys:")
            for key in sorted(common):
                cached_type = cached_schema[key]
                search_type = search_schema[key]
                match = "✅" if cached_type == search_type else "❌"
                print(f"  {match} {key:30s} cached={cached_type:20s} search={search_type:20s}")

    print("\n" + "="*80)


if __name__ == "__main__":
    try:
        compare_schemas()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
