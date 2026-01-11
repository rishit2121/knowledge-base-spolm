"""Example usage of the knowledge base system."""
import json
from datetime import datetime
from models.run import RunPayload
from models.retrieval import RetrievalRequest
from memory_builder import MemoryBuilder
from memory_retrieval import MemoryRetrieval


def example_run_payload():
    """Example run payload for testing."""
    return RunPayload(
        run_id="run_001",
        task_text="Create a user authentication system with JWT tokens",
        agent_id="agent_001",
        run_tree={
            "steps": [
                {
                    "type": "reference",
                    "source": "schema",
                    "content": "User schema with email and password fields"
                },
                {
                    "type": "reference",
                    "source": "api_response",
                    "content": "JWT library documentation"
                },
                {
                    "type": "artifact",
                    "type": "code",
                    "content": "def authenticate_user(email, password): ..."
                },
                {
                    "type": "artifact",
                    "type": "schema",
                    "content": "Token schema definition"
                }
            ],
            "reasoning": "Need to implement secure authentication",
            "tools_used": ["code_generator", "schema_validator"]
        },
        outcome="success",
        created_at=datetime.utcnow()
    )


def example_process_run():
    """Example: Process a completed run."""
    print("=" * 60)
    print("Example: Processing a Run")
    print("=" * 60)
    
    builder = MemoryBuilder()
    payload = example_run_payload()
    
    result = builder.process_run(payload)
    print(json.dumps(result, indent=2, default=str))
    print("\n✓ Run processed successfully!\n")


def example_retrieve_memory():
    """Example: Retrieve memory for a task."""
    print("=" * 60)
    print("Example: Retrieving Memory")
    print("=" * 60)
    
    retrieval = MemoryRetrieval()
    request = RetrievalRequest(
        task_text="I need to implement user authentication",
        agent_id="agent_001",
        top_k=3
    )
    
    response = retrieval.retrieve(request)
    
    print(f"Confidence: {response.confidence}")
    print(f"\nObservations:")
    for obs in response.observations:
        print(f"  - {obs}")
    
    print(f"\nRelated Runs ({len(response.related_runs)}):")
    for run in response.related_runs:
        print(f"\n  Run ID: {run.run_id}")
        print(f"  Outcome: {run.outcome}")
        print(f"  Similarity: {run.similarity_score:.3f}")
        print(f"  Summary: {run.summary[:100]}...")
        print(f"  References: {len(run.references)}")
        print(f"  Artifacts: {len(run.artifacts)}")
    
    print("\n✓ Memory retrieved successfully!\n")


if __name__ == "__main__":
    print("\nKnowledge Base Example Usage\n")
    
    try:
        # Example 1: Process a run
        example_process_run()
        
        # Example 2: Retrieve memory
        example_retrieve_memory()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

