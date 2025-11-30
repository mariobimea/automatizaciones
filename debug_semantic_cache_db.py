#!/usr/bin/env python3
"""
Debug queries para ver qué se está guardando en el semantic cache.
"""

import json
import psycopg2
from psycopg2.extras import RealDictCursor


def connect_db():
    """Connect to production database"""
    return psycopg2.connect(
        "postgresql://postgres:KEeNOLKQWzndcAzbXAMAXzxJJrhGmPbM@trolley.proxy.rlwy.net:23108/railway"
    )


def query_1_recent_chain_of_work():
    """
    Query 1: Ver últimos 5 Chain of Work entries con semantic cache search
    """
    print("\n" + "="*80)
    print("QUERY 1: Últimos 5 Chain of Work con semantic cache search")
    print("="*80)

    conn = connect_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    query = """
    SELECT
        id,
        execution_id,
        node_id,
        node_type,
        input_context,
        output_result,
        ai_metadata,
        timestamp,
        status
    FROM chain_of_work
    WHERE ai_metadata::text LIKE '%semantic_cache_search%'
    ORDER BY timestamp DESC
    LIMIT 5
    """

    cur.execute(query)
    rows = cur.fetchall()

    print(f"\nTotal: {len(rows)} entries\n")

    for i, row in enumerate(rows, 1):
        print(f"\n{'='*80}")
        print(f"Entry {i}")
        print(f"{'='*80}")
        print(f"ID: {row['id']}")
        print(f"Execution ID: {row['execution_id']}")
        print(f"Node ID: {row['node_id']}")
        print(f"Node Type: {row['node_type']}")
        print(f"Status: {row['status']}")
        print(f"Timestamp: {row['timestamp']}")

        # Extract semantic cache search from ai_metadata
        ai_metadata = row['ai_metadata']
        if isinstance(ai_metadata, str):
            ai_metadata = json.loads(ai_metadata)

        semantic_search = ai_metadata.get('semantic_cache_search', {})

        if semantic_search:
            print(f"\n📊 Semantic Cache Search:")
            print(f"   Threshold: {semantic_search.get('threshold')}")
            print(f"   Top K: {semantic_search.get('top_k')}")

            # Show query (truncated)
            query_text = semantic_search.get('query', '')
            if query_text:
                print(f"\n   Query (first 300 chars):")
                print(f"   {query_text[:300]}")
                if len(query_text) > 300:
                    print(f"   ... (total: {len(query_text)} chars)")

            # Show available keys
            available_keys = semantic_search.get('available_keys', [])
            all_available_keys = semantic_search.get('all_available_keys', [])

            print(f"\n   Available keys: {available_keys}")
            print(f"   All available keys: {all_available_keys}")

            # Show results
            results_above = semantic_search.get('results_above_threshold', [])
            all_results = semantic_search.get('all_results', [])

            print(f"\n   Results above threshold: {len(results_above)}")
            print(f"   Total results: {len(all_results)}")

            if results_above:
                print(f"\n   ✅ Matches found:")
                for j, match in enumerate(results_above[:2], 1):
                    print(f"\n      Match {j}:")
                    print(f"         Score: {match.get('score')}")
                    print(f"         Action: {match.get('node_action')}")
                    print(f"         Required keys: {match.get('required_keys')}")

                    # Show input schema from match
                    match_schema = match.get('input_schema', {})
                    if match_schema:
                        print(f"         Input schema: {match_schema}")
            else:
                print(f"\n   ❌ No matches above threshold")

                if all_results:
                    best = all_results[0]
                    print(f"\n   Best result (below threshold):")
                    print(f"      Score: {best.get('score')}")
                    print(f"      Action: {best.get('node_action')}")
                    print(f"      Required keys: {best.get('required_keys')}")

            # Check if code was saved
            cache_meta = ai_metadata.get('cache_metadata', {})
            if cache_meta:
                print(f"\n   Cache metadata:")
                print(f"      Saved for future: {cache_meta.get('saved_for_future', False)}")
                print(f"      Cache key: {cache_meta.get('cache_key', 'N/A')}")

    cur.close()
    conn.close()


def query_2_same_workflow_multiple_times():
    """
    Query 2: Ver workflows que se ejecutaron múltiples veces
    """
    print("\n" + "="*80)
    print("QUERY 2: Workflows ejecutados múltiples veces")
    print("="*80)

    conn = connect_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    query = """
    SELECT
        e.workflow_id,
        cw.node_id,
        cw.node_type,
        COUNT(*) as execution_count,
        MIN(cw.timestamp) as first_execution,
        MAX(cw.timestamp) as last_execution
    FROM chain_of_work cw
    JOIN executions e ON cw.execution_id = e.id
    WHERE cw.ai_metadata::text LIKE '%semantic_cache_search%'
    GROUP BY e.workflow_id, cw.node_id, cw.node_type
    HAVING COUNT(*) >= 2
    ORDER BY execution_count DESC
    LIMIT 5
    """

    cur.execute(query)
    rows = cur.fetchall()

    print(f"\nTotal: {len(rows)} workflows/nodes ejecutados múltiples veces\n")

    if not rows:
        print("❌ No hay workflows ejecutados múltiples veces (todavía)")
        cur.close()
        conn.close()
        return

    for i, row in enumerate(rows, 1):
        print(f"\n{'-'*80}")
        print(f"Workflow/Node {i}")
        print(f"{'-'*80}")
        print(f"Workflow ID: {row['workflow_id']}")
        print(f"Node ID: {row['node_id']}")
        print(f"Node Type: {row['node_type']}")
        print(f"Executions: {row['execution_count']}")
        print(f"First: {row['first_execution']}")
        print(f"Last: {row['last_execution']}")

    cur.close()
    conn.close()


def query_3_input_schemas_from_same_workflow():
    """
    Query 3: Comparar input_schemas de un mismo workflow ejecutado varias veces
    """
    print("\n" + "="*80)
    print("QUERY 3: Comparar input_schemas entre ejecuciones del mismo workflow")
    print("="*80)

    conn = connect_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    # First find a workflow executed multiple times
    query = """
    SELECT
        e.workflow_id,
        cw.node_id,
        ARRAY_AGG(cw.id ORDER BY cw.timestamp) as cw_ids
    FROM chain_of_work cw
    JOIN executions e ON cw.execution_id = e.id
    WHERE cw.ai_metadata::text LIKE '%semantic_cache_search%'
    GROUP BY e.workflow_id, cw.node_id
    HAVING COUNT(*) >= 2
    LIMIT 1
    """

    cur.execute(query)
    result = cur.fetchone()

    if not result:
        print("❌ No hay workflows ejecutados múltiples veces para comparar")
        cur.close()
        conn.close()
        return

    workflow_id = result['workflow_id']
    node_id = result['node_id']
    cw_ids = result['cw_ids']

    print(f"\nWorkflow ID: {workflow_id}")
    print(f"Node ID: {node_id}")
    print(f"Executions: {len(cw_ids)}")

    # Get all executions
    cur.execute("""
        SELECT id, ai_metadata, timestamp
        FROM chain_of_work
        WHERE id = ANY(%s)
        ORDER BY timestamp
    """, (cw_ids,))

    executions = cur.fetchall()

    schemas = []
    queries = []

    for i, exec_row in enumerate(executions, 1):
        print(f"\n{'-'*80}")
        print(f"Execution {i} - {exec_row['timestamp']}")
        print(f"{'-'*80}")

        ai_metadata = exec_row['ai_metadata']
        if isinstance(ai_metadata, str):
            ai_metadata = json.loads(ai_metadata)

        semantic_search = ai_metadata.get('semantic_cache_search', {})

        # Extract query and schema
        query_text = semantic_search.get('query', '')
        available_keys = semantic_search.get('available_keys', [])

        queries.append(query_text)

        print(f"Available keys: {available_keys}")

        # Try to extract schema from query
        if 'Input Schema:' in query_text:
            schema_part = query_text.split('Input Schema:')[1].strip()
            print(f"\nInput Schema in query:")
            print(schema_part[:300])
            schemas.append(schema_part)

    # Compare schemas
    print(f"\n{'='*80}")
    print("COMPARISON")
    print(f"{'='*80}")

    if len(schemas) >= 2:
        if schemas[0] == schemas[1]:
            print("✅ Schemas are IDENTICAL between executions")
        else:
            print("❌ Schemas are DIFFERENT between executions")
            print("\nSchema 1 (first 200 chars):")
            print(schemas[0][:200])
            print("\nSchema 2 (first 200 chars):")
            print(schemas[1][:200])

    if len(queries) >= 2:
        if queries[0] == queries[1]:
            print("\n✅ Complete queries are IDENTICAL")
        else:
            print("\n❌ Complete queries are DIFFERENT")
            print(f"\nQuery 1 length: {len(queries[0])}")
            print(f"Query 2 length: {len(queries[1])}")

    cur.close()
    conn.close()


def query_4_all_results_scores():
    """
    Query 4: Ver todos los scores de all_results para entender el threshold
    """
    print("\n" + "="*80)
    print("QUERY 4: Scores de todos los resultados (para analizar threshold)")
    print("="*80)

    conn = connect_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    query = """
    SELECT
        id,
        node_id,
        node_type,
        ai_metadata,
        timestamp
    FROM chain_of_work
    WHERE ai_metadata::text LIKE '%all_results%'
    ORDER BY timestamp DESC
    LIMIT 3
    """

    cur.execute(query)
    rows = cur.fetchall()

    print(f"\nTotal: {len(rows)} entries con all_results\n")

    for i, row in enumerate(rows, 1):
        print(f"\n{'='*80}")
        print(f"Entry {i} - {row['node_type']}")
        print(f"{'='*80}")
        print(f"Timestamp: {row['timestamp']}")

        ai_metadata = row['ai_metadata']
        if isinstance(ai_metadata, str):
            ai_metadata = json.loads(ai_metadata)

        semantic_search = ai_metadata.get('semantic_cache_search', {})
        all_results = semantic_search.get('all_results', [])

        if all_results:
            print(f"\nTotal results: {len(all_results)}")
            print(f"\nScores distribution:")

            for j, result in enumerate(all_results[:10], 1):
                score = result.get('score', 0)
                action = result.get('node_action', 'unknown')
                above = result.get('above_threshold', False)
                required = result.get('required_keys', [])

                status = "✅" if above else "❌"
                print(f"   {status} {j}. Score: {score:.3f} | Action: {action} | Required: {required}")

    cur.close()
    conn.close()


if __name__ == "__main__":
    print("\n🔍 DEBUGGING SEMANTIC CACHE - QUERIES A LA BASE DE DATOS")

    try:
        query_1_recent_chain_of_work()
        query_2_same_workflow_multiple_times()
        query_3_input_schemas_from_same_workflow()
        query_4_all_results_scores()

        print("\n" + "="*80)
        print("✅ QUERIES COMPLETADAS")
        print("="*80 + "\n")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
