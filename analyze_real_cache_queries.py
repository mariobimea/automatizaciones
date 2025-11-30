#!/usr/bin/env python3
"""
Analizar queries reales de semantic cache desde Chain of Work.

Este script:
1. Lee los Chain of Work entries desde PostgreSQL
2. Extrae los semantic_cache_search metadata
3. Compara los queries de búsqueda vs lo que debería guardarse
4. Identifica diferencias que causan que no haya matches
"""

import json
import os
import psycopg2
from psycopg2.extras import RealDictCursor


def connect_db():
    """Connect to production database"""
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        db_url = "postgresql://postgres:KEeNOLKQWzndcAzbXAMAXzxJJrhGmPbM@trolley.proxy.rlwy.net:23108/railway"

    conn = psycopg2.connect(db_url)
    return conn


def analyze_recent_workflows():
    """
    Analizar los últimos workflows ejecutados.
    """
    print("\n" + "="*80)
    print("ANALYZING REAL WORKFLOW SEMANTIC CACHE QUERIES")
    print("="*80)

    conn = connect_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    # Get recent chain of work entries with semantic cache metadata
    query = """
    SELECT
        cw.id,
        cw.execution_id,
        cw.node_id,
        cw.action,
        cw.execution_metadata,
        cw.created_at,
        e.workflow_id
    FROM chain_of_work cw
    JOIN executions e ON cw.execution_id = e.id
    WHERE cw.execution_metadata::text LIKE '%semantic_cache_search%'
    ORDER BY cw.created_at DESC
    LIMIT 10
    """

    cur.execute(query)
    entries = cur.fetchall()

    print(f"\nFound {len(entries)} Chain of Work entries with semantic cache searches\n")

    for i, entry in enumerate(entries, 1):
        print(f"\n{'='*80}")
        print(f"Entry {i}: {entry['action']} (Node: {entry['node_id']})")
        print(f"Created: {entry['created_at']}")
        print(f"{'='*80}")

        metadata = entry['execution_metadata']

        # Extract semantic cache search metadata
        if isinstance(metadata, str):
            metadata = json.loads(metadata)

        ai_metadata = metadata.get('ai_metadata', {})
        semantic_search = ai_metadata.get('semantic_cache_search', {})

        if not semantic_search:
            print("⚠️  No semantic_cache_search metadata found")
            continue

        # Show search details
        print(f"\n📊 Search Details:")
        print(f"   Threshold: {semantic_search.get('threshold', 'N/A')}")
        print(f"   Available keys: {semantic_search.get('available_keys', [])}")
        print(f"   All available keys: {semantic_search.get('all_available_keys', [])}")

        # Show query
        query_text = semantic_search.get('query', '')
        if query_text:
            print(f"\n🔍 Search Query:")
            # Truncate if too long
            if len(query_text) > 500:
                print(f"{query_text[:500]}...")
                print(f"   (truncated, total length: {len(query_text)})")
            else:
                print(query_text)

        # Show results
        results_above = semantic_search.get('results_above_threshold', [])
        all_results = semantic_search.get('all_results', [])

        print(f"\n📈 Results:")
        print(f"   Above threshold (0.85): {len(results_above)}")
        print(f"   Total results: {len(all_results)}")

        if results_above:
            print(f"\n   ✅ Matches found:")
            for j, result in enumerate(results_above[:3], 1):
                print(f"\n      Match {j}:")
                print(f"         Score: {result.get('score', 'N/A')}")
                print(f"         Action: {result.get('node_action', 'N/A')}")
                print(f"         Description: {result.get('node_description', 'N/A')[:60]}...")
                print(f"         Required keys: {result.get('required_keys', [])}")

                # Show code preview if available
                code = result.get('code', '')
                if code:
                    print(f"         Code preview: {code[:80]}...")
        else:
            print(f"\n   ❌ No matches above threshold")

            if all_results:
                print(f"\n   📉 Best result below threshold:")
                best = all_results[0]
                print(f"      Score: {best.get('score', 'N/A')}")
                print(f"      Action: {best.get('node_action', 'N/A')}")
                print(f"      Required keys: {best.get('required_keys', [])}")
                print(f"      Code preview: {best.get('code', '')[:80]}...")

        # Check if code was saved
        cache_metadata = metadata.get('cache_metadata', {})
        if cache_metadata.get('saved_for_future'):
            print(f"\n   💾 Code was saved to cache for future use")

    cur.close()
    conn.close()


def compare_save_vs_search():
    """
    Comparar lo que se guarda vs lo que se busca.

    Para el mismo workflow ejecutado 2 veces:
    - Primera vez: genera código y lo guarda
    - Segunda vez: busca el código guardado

    ¿El query de búsqueda coincide con lo que se guardó?
    """
    print("\n" + "="*80)
    print("COMPARING SAVE VS SEARCH FOR SAME WORKFLOW")
    print("="*80)

    conn = connect_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    # Find workflows executed multiple times (same workflow_id, same node_id)
    query = """
    WITH node_executions AS (
        SELECT
            e.workflow_id,
            cw.node_id,
            cw.action,
            COUNT(*) as execution_count,
            ARRAY_AGG(cw.id ORDER BY cw.created_at) as cw_ids,
            ARRAY_AGG(cw.created_at ORDER BY cw.created_at) as timestamps
        FROM chain_of_work cw
        JOIN executions e ON cw.execution_id = e.id
        WHERE cw.execution_metadata::text LIKE '%semantic_cache_search%'
        GROUP BY e.workflow_id, cw.node_id, cw.action
        HAVING COUNT(*) >= 2
    )
    SELECT * FROM node_executions
    ORDER BY execution_count DESC
    LIMIT 5
    """

    cur.execute(query)
    repeated_nodes = cur.fetchall()

    if not repeated_nodes:
        print("\n⚠️  No repeated node executions found")
        cur.close()
        conn.close()
        return

    print(f"\nFound {len(repeated_nodes)} nodes executed multiple times\n")

    for node_info in repeated_nodes:
        workflow_id = node_info['workflow_id']
        node_id = node_info['node_id']
        action = node_info['action']
        exec_count = node_info['execution_count']
        cw_ids = node_info['cw_ids']

        print(f"\n{'='*80}")
        print(f"Workflow: {workflow_id}, Node: {node_id}")
        print(f"Action: {action}")
        print(f"Executed {exec_count} times")
        print(f"{'='*80}")

        # Get first and last execution
        first_cw_id = cw_ids[0]
        last_cw_id = cw_ids[-1]

        # Fetch both executions
        cur.execute("""
            SELECT id, execution_metadata, created_at
            FROM chain_of_work
            WHERE id IN %s
            ORDER BY created_at
        """, ([first_cw_id, last_cw_id],))

        executions = cur.fetchall()

        if len(executions) < 2:
            continue

        first_exec = executions[0]
        last_exec = executions[-1]

        print(f"\n📅 First execution: {first_exec['created_at']}")
        print(f"📅 Last execution: {last_exec['created_at']}")

        # Extract search query from both
        first_meta = json.loads(first_exec['execution_metadata']) if isinstance(first_exec['execution_metadata'], str) else first_exec['execution_metadata']
        last_meta = json.loads(last_exec['execution_metadata']) if isinstance(last_exec['execution_metadata'], str) else last_exec['execution_metadata']

        first_search = first_meta.get('ai_metadata', {}).get('semantic_cache_search', {})
        last_search = last_meta.get('ai_metadata', {}).get('semantic_cache_search', {})

        first_query = first_search.get('query', '')
        last_query = last_search.get('query', '')

        # Compare queries
        if first_query == last_query:
            print(f"\n   ✅ Queries are IDENTICAL")
            print(f"      Query length: {len(first_query)} chars")
        else:
            print(f"\n   ❌ Queries are DIFFERENT")
            print(f"      First query length: {len(first_query)} chars")
            print(f"      Last query length: {len(last_query)} chars")

            # Show difference
            print(f"\n      First query preview:")
            print(f"      {first_query[:200]}...")
            print(f"\n      Last query preview:")
            print(f"      {last_query[:200]}...")

        # Check if last execution found code from first
        last_results = last_search.get('results_above_threshold', [])
        if last_results:
            print(f"\n   ✅ Found {len(last_results)} matches in second execution")
        else:
            print(f"\n   ❌ No matches found in second execution (should have found code from first!)")

    cur.close()
    conn.close()


if __name__ == "__main__":
    try:
        analyze_recent_workflows()
        compare_save_vs_search()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
