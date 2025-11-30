#!/usr/bin/env python3
"""
Ver códigos que se EJECUTARON (desde Chain of Work).
Esto muestra qué códigos se generaron y ejecutaron, aunque no estén en el cache.
"""

import json
import psycopg2
from psycopg2.extras import RealDictCursor


def connect_db():
    """Connect to production database"""
    return psycopg2.connect(
        "postgresql://postgres:KEeNOLKQWzndcAzbXAMAXzxJJrhGmPbM@trolley.proxy.rlwy.net:23108/railway"
    )


def view_executed_codes():
    """
    Ver todos los códigos que se ejecutaron exitosamente.
    """
    print("\n" + "="*80)
    print("CÓDIGOS EJECUTADOS (desde Chain of Work)")
    print("="*80)

    conn = connect_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    # Get all successful action nodes with code
    query = """
    SELECT
        cw.id,
        cw.execution_id,
        cw.node_id,
        cw.code_executed,
        cw.input_context,
        cw.output_result,
        cw.ai_metadata,
        cw.status,
        cw.timestamp,
        e.workflow_id
    FROM chain_of_work cw
    JOIN executions e ON cw.execution_id = e.id
    WHERE cw.node_type = 'action'
      AND cw.status = 'success'
      AND cw.code_executed IS NOT NULL
      AND cw.code_executed != ''
    ORDER BY cw.timestamp DESC
    LIMIT 20
    """

    cur.execute(query)
    rows = cur.fetchall()

    print(f"\nTotal: {len(rows)} códigos ejecutados (últimos 20)\n")

    if len(rows) == 0:
        print("❌ No hay códigos ejecutados")
        cur.close()
        conn.close()
        return

    for i, row in enumerate(rows, 1):
        print(f"\n{'='*80}")
        print(f"Code #{i}")
        print(f"{'='*80}")
        print(f"Workflow ID: {row['workflow_id']}")
        print(f"Execution ID: {row['execution_id']}")
        print(f"Node ID: {row['node_id']}")
        print(f"Status: {row['status']}")
        print(f"Timestamp: {row['timestamp']}")

        # Input context (schema)
        input_context = row['input_context']
        if input_context:
            if isinstance(input_context, str):
                input_context = json.loads(input_context)

            print(f"\nInput Context Keys:")
            for key in sorted(input_context.keys()):
                # Don't print values, just keys and types
                value = input_context[key]
                type_str = type(value).__name__
                if isinstance(value, str) and len(value) > 50:
                    type_str = f"str({len(value)})"
                elif isinstance(value, list):
                    type_str = f"list({len(value)})"
                elif isinstance(value, dict):
                    type_str = f"dict({len(value)})"

                print(f"   {key}: {type_str}")

        # Output result
        output_result = row['output_result']
        if output_result:
            if isinstance(output_result, str):
                try:
                    output_result = json.loads(output_result)
                except:
                    pass

            print(f"\nOutput Keys:")
            if isinstance(output_result, dict):
                for key in sorted(output_result.keys()):
                    print(f"   {key}")

        # AI metadata (to see if it was cached)
        ai_metadata = row['ai_metadata']
        if ai_metadata:
            if isinstance(ai_metadata, str):
                ai_metadata = json.loads(ai_metadata)

            # Check if semantic cache was used
            semantic_search = ai_metadata.get('semantic_cache_search', {})
            if semantic_search:
                results_above = semantic_search.get('results_above_threshold', [])
                if results_above:
                    print(f"\n✅ Used CACHED code (score: {results_above[0].get('score', 0):.3f})")
                else:
                    print(f"\n🔄 Generated NEW code (no cache hit)")

            # Check if code was saved to cache
            cache_meta = ai_metadata.get('cache_metadata', {})
            if cache_meta and cache_meta.get('saved_for_future'):
                print(f"💾 Code SAVED to semantic cache")

        # Code
        code = row['code_executed']
        print(f"\n📄 Code ({len(code)} chars):")
        print("-" * 80)
        print(code)
        print("-" * 80)

    cur.close()
    conn.close()


def count_cache_hits_vs_misses():
    """
    Contar cuántas veces se usó el cache vs se generó código nuevo.
    """
    print("\n" + "="*80)
    print("CACHE HITS vs MISSES")
    print("="*80)

    conn = connect_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    query = """
    SELECT
        cw.id,
        cw.ai_metadata
    FROM chain_of_work cw
    WHERE cw.node_type = 'action'
      AND cw.status = 'success'
      AND cw.ai_metadata::text LIKE '%semantic_cache_search%'
    ORDER BY cw.timestamp DESC
    LIMIT 100
    """

    cur.execute(query)
    rows = cur.fetchall()

    cache_hits = 0
    cache_misses = 0
    codes_saved = 0

    for row in rows:
        ai_metadata = row['ai_metadata']
        if isinstance(ai_metadata, str):
            ai_metadata = json.loads(ai_metadata)

        semantic_search = ai_metadata.get('semantic_cache_search', {})
        results_above = semantic_search.get('results_above_threshold', [])

        if results_above:
            cache_hits += 1
        else:
            cache_misses += 1

        cache_meta = ai_metadata.get('cache_metadata', {})
        if cache_meta and cache_meta.get('saved_for_future'):
            codes_saved += 1

    total = cache_hits + cache_misses

    print(f"\nTotal executions analyzed: {total}")
    print(f"\n✅ Cache HITS: {cache_hits} ({cache_hits/total*100:.1f}%)" if total > 0 else "")
    print(f"❌ Cache MISSES: {cache_misses} ({cache_misses/total*100:.1f}%)" if total > 0 else "")
    print(f"💾 Codes SAVED: {codes_saved}")

    cur.close()
    conn.close()


if __name__ == "__main__":
    try:
        view_executed_codes()
        count_cache_hits_vs_misses()

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
