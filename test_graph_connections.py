"""Test graph connections and retrieval ranking."""
from datetime import datetime
from models.run import RunPayload
from models.retrieval import RetrievalRequest
from memory_builder import MemoryBuilder
from memory_retrieval import MemoryRetrieval
from db.connection import get_neo4j_driver


def add_run_1():
    """Add first successful run about REST API."""
    print("=" * 70)
    print("STEP 1: Adding First Successful Run (REST API)")
    print("=" * 70)
    
    payload = RunPayload(
        run_id=f"test_run_api_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        task_text="Build a REST API endpoint for user profile management with CRUD operations",
        agent_id="test_agent",
        run_tree={
            "steps": [
                {
                    "type": "reference",
                    "source": "schema",
                    "content": "User profile schema: id, name, email, bio, avatar_url"
                },
                {
                    "type": "artifact",
                    "type": "code",
                    "content": "@app.get('/users/{user_id}') async def get_user(user_id: int): ..."
                }
            ],
            "reasoning": "Need RESTful API endpoints for user profile management",
            "tools_used": ["fastapi", "sqlalchemy"]
        },
        outcome="success",
        created_at=datetime.now(datetime.timezone.utc) if hasattr(datetime, 'timezone') else datetime.utcnow()
    )
    
    builder = MemoryBuilder()
    result = builder.process_run(payload)
    
    if result.get("success"):
        print(f"✅ Run 1 added: {payload.run_id}")
        print(f"   Task: {payload.task_text}")
        return payload.run_id
    else:
        print(f"❌ Failed: {result.get('error')}")
        return None


def add_run_2():
    """Add second successful run about database queries."""
    print("\n" + "=" * 70)
    print("STEP 2: Adding Second Successful Run (Database Queries)")
    print("=" * 70)
    
    payload = RunPayload(
        run_id=f"test_run_db_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        task_text="Create optimized database queries for fetching user data with joins and filters",
        agent_id="test_agent",
        run_tree={
            "steps": [
                {
                    "type": "reference",
                    "source": "schema",
                    "content": "Database schema: users, profiles, preferences tables"
                },
                {
                    "type": "artifact",
                    "type": "code",
                    "content": "SELECT u.*, p.bio FROM users u JOIN profiles p ON u.id = p.user_id WHERE u.active = 1"
                }
            ],
            "reasoning": "Need efficient database queries with proper joins",
            "tools_used": ["sqlalchemy", "postgresql"]
        },
        outcome="success",
        created_at=datetime.now(datetime.timezone.utc) if hasattr(datetime, 'timezone') else datetime.utcnow()
    )
    
    builder = MemoryBuilder()
    result = builder.process_run(payload)
    
    if result.get("success"):
        print(f"✅ Run 2 added: {payload.run_id}")
        print(f"   Task: {payload.task_text}")
        return payload.run_id
    else:
        print(f"❌ Failed: {result.get('error')}")
        return None


def check_outcome_connections(run_id_1: str, run_id_2: str):
    """Check if both runs connect to the same Outcome node."""
    print("\n" + "=" * 70)
    print("STEP 3: Checking Graph Connections")
    print("=" * 70)
    
    driver = get_neo4j_driver()
    with driver.session() as session:
        # Check if both runs connect to the same Outcome node
        result = session.run("""
            MATCH (r1:Run {id: $run_id_1})-[:ENDED_WITH]->(o:Outcome)
            MATCH (r2:Run {id: $run_id_2})-[:ENDED_WITH]->(o)
            RETURN o.label AS outcome_label, 
                   count(DISTINCT r1) + count(DISTINCT r2) AS total_runs
        """, run_id_1=run_id_1, run_id_2=run_id_2)
        
        record = result.single()
        if record:
            print(f"✅ Both runs connect to the same Outcome node!")
            print(f"   Outcome: {record['outcome_label']}")
            print(f"   Total runs with this outcome: {record['total_runs']}")
        else:
            print("⚠️  Runs don't share the same Outcome node (this is unexpected)")
        
        # Count all runs connected to "success" outcome
        result = session.run("""
            MATCH (r:Run)-[:ENDED_WITH]->(o:Outcome {label: 'success'})
            RETURN count(r) AS success_count
        """)
        record = result.single()
        if record:
            print(f"   Total successful runs in graph: {record['success_count']}")


def test_retrieval_ranking(run_id_1: str, run_id_2: str):
    """Test retrieval with a query similar to run 1, verify it ranks higher."""
    print("\n" + "=" * 70)
    print("STEP 4: Testing Retrieval Ranking")
    print("=" * 70)
    
    retrieval = MemoryRetrieval()
    
    # Query that's more similar to run 1 (REST API) than run 2 (database queries)
    request = RetrievalRequest(
        task_text="I need to create API endpoints for managing user profiles",
        agent_id="test_agent",
        top_k=5
    )
    
    print(f"\n🔍 Query: '{request.task_text}'")
    print(f"   Expected: Run 1 (REST API) should rank higher than Run 2 (Database)")
    
    response = retrieval.retrieve(request)
    
    print(f"\n✅ Found {len(response.related_runs)} related run(s)")
    print(f"   Confidence: {response.confidence:.2%}")
    
    print(f"\n📊 Ranking Results:")
    print("-" * 70)
    
    found_run_1 = False
    found_run_2 = False
    run_1_rank = None
    run_2_rank = None
    
    for i, run in enumerate(response.related_runs, 1):
        is_run_1 = run.run_id == run_id_1
        is_run_2 = run.run_id == run_id_2
        
        if is_run_1:
            found_run_1 = True
            run_1_rank = i
        if is_run_2:
            found_run_2 = True
            run_2_rank = i
        
        marker = ""
        if is_run_1:
            marker = " ⭐ (Run 1 - REST API)"
        elif is_run_2:
            marker = " 🔹 (Run 2 - Database)"
        
        print(f"\n   Rank {i}:")
        print(f"   - ID: {run.run_id}{marker}")
        print(f"   - Similarity: {run.similarity_score:.4f}")
        print(f"   - Outcome: {run.outcome}")
        print(f"   - Summary: {run.summary[:100]}...")
    
    print("\n" + "-" * 70)
    
    # Verify ranking
    if found_run_1 and found_run_2:
        if run_1_rank < run_2_rank:
            print(f"\n🎉 SUCCESS! Correct ranking!")
            print(f"   Run 1 (REST API) ranked #{run_1_rank}, Run 2 (Database) ranked #{run_2_rank}")
            print(f"   ✅ The more similar run (Run 1) is ranked higher!")
        else:
            print(f"\n⚠️  Ranking issue:")
            print(f"   Run 1 (REST API) ranked #{run_1_rank}, Run 2 (Database) ranked #{run_2_rank}")
            print(f"   ⚠️  Run 2 is ranked higher, but Run 1 should be more similar to the query")
    elif found_run_1:
        print(f"\n✅ Found Run 1 at rank #{run_1_rank}")
        print(f"   Run 2 was not in top results (may be below similarity threshold)")
    elif found_run_2:
        print(f"\n⚠️  Only found Run 2 at rank #{run_2_rank}")
        print(f"   Run 1 was not found (unexpected - it should be more similar)")
    else:
        print(f"\n⚠️  Neither test run was found in results")
        print(f"   This might mean other runs are more similar, or similarity threshold is too high")
    
    return response


def main():
    """Run the complete test."""
    print("\n" + "🧪 " * 35)
    print("GRAPH CONNECTIONS AND RANKING TEST")
    print("🧪 " * 35 + "\n")
    
    # Step 1: Add first run
    run_id_1 = add_run_1()
    if not run_id_1:
        print("\n❌ Failed to add first run, aborting test")
        return
    
    # Step 2: Add second run
    run_id_2 = add_run_2()
    if not run_id_2:
        print("\n❌ Failed to add second run, aborting test")
        return
    
    # Step 3: Check graph connections
    check_outcome_connections(run_id_1, run_id_2)
    
    # Step 4: Test retrieval ranking
    test_retrieval_ranking(run_id_1, run_id_2)
    
    print("\n" + "=" * 70)
    print("✅ TEST COMPLETE")
    print("=" * 70)
    print("\nCheck Neo4j Browser to see:")
    print("  - Both runs connected to the same 'success' Outcome node")
    print("  - Task nodes and their relationships")
    print("  - The graph structure growing with connections")


if __name__ == "__main__":
    main()

