"""Test script for the knowledge base system."""
import json
from datetime import datetime
from models.run import RunPayload
from models.retrieval import RetrievalRequest
from memory_builder import MemoryBuilder
from memory_retrieval import MemoryRetrieval
import config


def test_memory_builder():
    """Test processing and storing a run."""
    print("=" * 70)
    print("TEST 1: Processing and Storing a Run")
    print("=" * 70)
    
    # Create a realistic run payload
    run_payload = RunPayload(
        run_id=f"test_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        task_text="Create a user authentication system with JWT tokens and password hashing",
        agent_id="test_agent_001",
        run_tree={
            "steps": [
                {
                    "type": "reference",
                    "source": "schema",
                    "content": "User schema with email, password_hash, and created_at fields"
                },
                {
                    "type": "reference",
                    "source": "api_response",
                    "content": "JWT library documentation - use HS256 algorithm"
                },
                {
                    "type": "reference",
                    "source": "prior_run",
                    "content": "Previous authentication attempt that failed due to weak password validation"
                },
                {
                    "type": "artifact",
                    "type": "code",
                    "content": """
def authenticate_user(email: str, password: str) -> Optional[str]:
    user = db.get_user_by_email(email)
    if user and bcrypt.checkpw(password.encode(), user.password_hash):
        token = jwt.encode({'user_id': user.id}, SECRET_KEY, algorithm='HS256')
        return token
    return None
"""
                },
                {
                    "type": "artifact",
                    "type": "schema",
                    "content": "Token schema: {token: string, expires_at: datetime, user_id: int}"
                },
                {
                    "type": "artifact",
                    "type": "plan",
                    "content": "Authentication workflow: 1) Validate credentials 2) Generate JWT 3) Return token"
                }
            ],
            "reasoning": "Need secure authentication with JWT tokens. Previous attempt failed because passwords weren't hashed properly.",
            "tools_used": ["code_generator", "schema_validator", "jwt_library"],
            "execution_time": 45.2,
            "tokens_used": 1250
        },
        outcome="success",
        created_at=datetime.utcnow()
    )
    
    print(f"\n📝 Processing run: {run_payload.run_id}")
    print(f"   Task: {run_payload.task_text}")
    print(f"   Outcome: {run_payload.outcome}")
    
    try:
        builder = MemoryBuilder()
        result = builder.process_run(run_payload)
        
        if result.get("success"):
            print(f"\n✅ Run processed successfully!")
            print(f"   - Task ID: {result.get('task_id')}")
            print(f"   - References: {result.get('references_count')}")
            print(f"   - Artifacts: {result.get('artifacts_count')}")
            return run_payload.run_id
        else:
            print(f"\n❌ Error processing run: {result.get('error')}")
            return None
    except Exception as e:
        print(f"\n❌ Exception: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_memory_retrieval(run_id: str = None):
    """Test retrieving memory for a similar task."""
    print("\n" + "=" * 70)
    print("TEST 2: Retrieving Memory for Similar Task")
    print("=" * 70)
    
    retrieval = MemoryRetrieval()
    
    # Test with a similar but slightly different task
    request = RetrievalRequest(
        task_text="I need to implement user login with authentication tokens",
        agent_id="test_agent_001",
        top_k=3
    )
    
    print(f"\n🔍 Searching for similar runs...")
    print(f"   Query: {request.task_text}")
    print(f"   Top K: {request.top_k}")
    
    try:
        response = retrieval.retrieve(request)
        
        print(f"\n✅ Memory retrieved!")
        print(f"   Confidence: {response.confidence:.2%}")
        print(f"\n📊 Observations ({len(response.observations)}):")
        for i, obs in enumerate(response.observations, 1):
            print(f"   {i}. {obs}")
        
        print(f"\n📚 Related Runs ({len(response.related_runs)}):")
        for i, run in enumerate(response.related_runs, 1):
            print(f"\n   Run {i}:")
            print(f"   - ID: {run.run_id}")
            print(f"   - Similarity: {run.similarity_score:.3f}")
            print(f"   - Outcome: {run.outcome}")
            print(f"   - Summary: {run.summary[:150]}...")
            print(f"   - References: {len(run.references)}")
            print(f"   - Artifacts: {len(run.artifacts)}")
            if run.run_tree:
                print(f"   - Has full run_tree: ✅")
            else:
                print(f"   - Has full run_tree: ❌")
        
        return response
    except Exception as e:
        print(f"\n❌ Exception: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_multiple_runs():
    """Test storing multiple runs and retrieving them."""
    print("\n" + "=" * 70)
    print("TEST 3: Multiple Runs and Retrieval")
    print("=" * 70)
    
    builder = MemoryBuilder()
    
    # Store a few different runs
    runs = [
        {
            "run_id": f"test_run_failure_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "task_text": "Create a payment processing system",
            "outcome": "failure",
            "run_tree": {
                "steps": [
                    {"type": "reference", "source": "api_response", "content": "Payment gateway API docs"},
                    {"type": "artifact", "type": "code", "content": "payment_handler.py - had SSL errors"}
                ],
                "reasoning": "Tried to integrate payment gateway but SSL certificate validation failed",
                "error": "SSL certificate verification error"
            }
        },
        {
            "run_id": f"test_run_success_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "task_text": "Set up database connection pooling",
            "outcome": "success",
            "run_tree": {
                "steps": [
                    {"type": "reference", "source": "schema", "content": "Database connection schema"},
                    {"type": "artifact", "type": "code", "content": "pool_manager.py - working connection pool"}
                ],
                "reasoning": "Implemented connection pooling to handle concurrent requests",
                "tools_used": ["database_driver", "connection_pool"]
            }
        }
    ]
    
    stored_run_ids = []
    for run_data in runs:
        payload = RunPayload(
            run_id=run_data["run_id"],
            task_text=run_data["task_text"],
            agent_id="test_agent_001",
            run_tree=run_data["run_tree"],
            outcome=run_data["outcome"],
            created_at=datetime.utcnow()
        )
        
        result = builder.process_run(payload)
        if result.get("success"):
            print(f"✅ Stored: {run_data['task_text']} ({run_data['outcome']})")
            stored_run_ids.append(run_data["run_id"])
        else:
            print(f"❌ Failed: {run_data['task_text']} - {result.get('error')}")
    
    # Now retrieve
    print(f"\n🔍 Retrieving memory for 'database connection' task...")
    retrieval = MemoryRetrieval()
    request = RetrievalRequest(
        task_text="I need to connect to a database efficiently",
        top_k=5
    )
    
    response = retrieval.retrieve(request)
    print(f"✅ Found {len(response.related_runs)} related runs")
    print(f"   Confidence: {response.confidence:.2%}")


def main():
    """Run all tests."""
    print("\n" + "🧪 " * 35)
    print("KNOWLEDGE BASE TEST SUITE")
    print("🧪 " * 35)
    
    # Validate configuration
    try:
        config.Config.validate()
        print(f"\n✅ Configuration valid")
        print(f"   Provider: {config.Config.PROVIDER}")
        if config.Config.PROVIDER == "gemini":
            print(f"   Embedding Model: {config.Config.GEMINI_EMBEDDING_MODEL}")
            print(f"   Chat Model: {config.Config.GEMINI_CHAT_MODEL}")
        else:
            print(f"   Embedding Model: {config.Config.OPENAI_EMBEDDING_MODEL}")
            print(f"   Chat Model: {config.Config.OPENAI_CHAT_MODEL}")
    except Exception as e:
        print(f"\n❌ Configuration error: {e}")
        print("   Please check your .env file")
        return
    
    # Test 1: Store a run
    run_id = test_memory_builder()
    
    if run_id:
        # Test 2: Retrieve memory
        test_memory_retrieval(run_id)
    
    # Test 3: Multiple runs
    test_multiple_runs()
    
    print("\n" + "=" * 70)
    print("✅ ALL TESTS COMPLETE")
    print("=" * 70)
    print("\nNext steps:")
    print("1. Check Neo4j Browser to see the stored nodes")
    print("2. Try the API: python api.py")
    print("3. Query the API: curl http://localhost:8000/stats")


if __name__ == "__main__":
    main()

