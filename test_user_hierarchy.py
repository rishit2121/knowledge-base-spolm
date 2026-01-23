"""Test script for User-Agent-Run hierarchy."""
import requests
import json
from datetime import datetime

API_URL = "http://localhost:8000"


def test_add_run_with_user():
    """Test adding a run with user_id - using unique context to avoid NOT decision."""
    print("="*70)
    print("TEST 1: Add Run with user_id")
    print("="*70)
    
    # Use a completely different task to avoid similarity rejection
    unique_task = f"Build a machine learning pipeline for sentiment analysis of customer reviews using TensorFlow and deploy it to AWS Lambda with API Gateway integration"
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    payload = {
        "run_id": f"test_run_ml_{timestamp}",
        "agent_id": "ml_agent",
        "user_id": "user_001",
        "user_task": unique_task,
        "status": "complete",
        "steps": [
            {
                "step_id": "step1",
                "step_name": "data_preprocessing",
                "step_type": "tool_call",
                "step_input": {"action": "Load and clean customer review dataset"},
                "step_output": {"data": "Dataset loaded: 10,000 reviews processed"}
            },
            {
                "step_id": "step2",
                "step_name": "model_training",
                "step_type": "llm_call",
                "step_input": {"model": "BERT", "epochs": 5},
                "step_output": {"data": "Model trained with 95% accuracy"}
            },
            {
                "step_id": "step3",
                "step_name": "deployment",
                "step_type": "tool_call",
                "step_input": {"platform": "AWS Lambda"},
                "step_output": {"data": "Deployed to Lambda with API endpoint"}
            }
        ],
        "final_output": "ML sentiment analysis pipeline successfully deployed",
        "metadata": {
            "framework": "TensorFlow",
            "cloud_provider": "AWS",
            "deployment_type": "serverless"
        }
    }
    
    print(f"📝 Adding run with user_id={payload['user_id']}, agent_id={payload['agent_id']}")
    response = requests.post(f"{API_URL}/runs", json=payload, timeout=30)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        decision = data.get("data", {}).get("decision", "UNKNOWN")
        print(f"✅ Request successful - Decision: {decision}")
        
        if decision == "NOT":
            print("\n📊 Similar Runs Found:")
            similar_runs = data.get("data", {}).get("similar_runs", [])
            if similar_runs:
                for i, similar in enumerate(similar_runs, 1):
                    print(f"\n   [{i}] Run ID: {similar.get('run_id', 'N/A')}")
                    print(f"       Similarity: {similar.get('similarity', 0):.3f}")
                    print(f"       Outcome: {similar.get('outcome', 'N/A')}")
                    print(f"       Summary: {similar.get('summary', 'N/A')[:80]}...")
            else:
                print("   (No similar runs details available)")
            
            similarity_score = data.get("data", {}).get("similarity_score")
            if similarity_score:
                print(f"\n   Overall Similarity Score: {similarity_score:.3f}")
        
        print(f"\n   Reason: {data.get('data', {}).get('reason', 'N/A')}")
        return True
    else:
        print(f"❌ Failed: {response.text}")
        return False


def test_retrieve_with_user():
    """Test retrieving with user_id filter."""
    print("\n" + "="*70)
    print("TEST 2: Retrieve with user_id filter")
    print("="*70)
    
    payload = {
        "task_text": "machine learning sentiment analysis",
        "user_id": "user_001",
        "top_k": 5
    }
    
    print(f"🔍 Retrieving with user_id={payload['user_id']}")
    response = requests.post(f"{API_URL}/retrieve", json=payload, timeout=30)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Found {len(data.get('related_runs', []))} runs")
        print(f"   Confidence: {data.get('confidence', 0)}")
        print(f"   Observations: {len(data.get('observations', []))}")
        return True
    else:
        print(f"❌ Failed: {response.text}")
        return False


def test_retrieve_all_with_user():
    """Test retrieve_all with user_id filter."""
    print("\n" + "="*70)
    print("TEST 3: Retrieve All with user_id filter")
    print("="*70)
    
    print("🔍 Retrieving all runs for user_001")
    response = requests.get(f"{API_URL}/retrieve_all?user_id=user_001", timeout=30)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Total runs: {data.get('total_count', 0)}")
        for i, run in enumerate(data.get('runs', [])[:3], 1):
            print(f"\n   Run {i}:")
            print(f"     ID: {run.get('run_id')}")
            print(f"     User ID: {run.get('user_id')}")
            print(f"     Agent ID: {run.get('agent_id')}")
            print(f"     Summary: {run.get('summary', '')[:60]}...")
        return True
    else:
        print(f"❌ Failed: {response.text}")
        return False


def test_add_multiple_users():
    """Test adding runs for different users with unique contexts."""
    print("\n" + "="*70)
    print("TEST 4: Add Runs for Multiple Users")
    print("="*70)
    
    # Different unique tasks for each user to avoid similarity rejection
    user_tasks = {
        "user_001": "Design and implement a real-time chat application using WebSockets, Redis pub/sub, and Node.js with message encryption",
        "user_002": "Create a blockchain-based supply chain tracking system using Solidity smart contracts and deploy to Ethereum testnet"
    }
    
    users = ["user_001", "user_002"]
    results = []
    
    for user_id in users:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        payload = {
            "run_id": f"test_run_{user_id}_{timestamp}",
            "agent_id": f"specialized_agent_{user_id}",
            "user_id": user_id,
            "user_task": user_tasks[user_id],
            "status": "complete",
            "steps": [
                {
                    "step_id": "step1",
                    "step_name": "architecture_design",
                    "step_type": "llm_call",
                    "step_input": {"task": user_tasks[user_id]},
                    "step_output": {"data": "Architecture designed successfully"}
                },
                {
                    "step_id": "step2",
                    "step_name": "implementation",
                    "step_type": "tool_call",
                    "step_input": {"action": "Implement core functionality"},
                    "step_output": {"data": "Implementation completed"}
                }
            ],
            "final_output": f"Successfully completed task for {user_id}",
            "metadata": {
                "user": user_id,
                "complexity": "high",
                "domain": "distributed_systems" if user_id == "user_001" else "blockchain"
            }
        }
        
        print(f"📝 Adding run for user_id={user_id}")
        print(f"   Task: {user_tasks[user_id][:60]}...")
        response = requests.post(f"{API_URL}/runs", json=payload, timeout=30)
        success = response.status_code == 200
        if success:
            result_data = response.json()
            decision = result_data.get("data", {}).get("decision", "UNKNOWN")
            print(f"   ✅ Success - Decision: {decision}")
            
            if decision == "NOT":
                similar_runs = result_data.get("data", {}).get("similar_runs", [])
                if similar_runs:
                    best_match = similar_runs[0]
                    print(f"      Similar to: {best_match.get('run_id', 'N/A')} (similarity: {best_match.get('similarity', 0):.3f})")
        else:
            print(f"   ❌ Failed: {response.text[:200]}")
        results.append(success)
    
    return all(results)


def check_api_health():
    """Check if API is running."""
    try:
        response = requests.get(f"{API_URL}/", timeout=5)
        return response.status_code == 200
    except:
        return False


def main():
    """Run all tests."""
    print("🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪")
    print("USER-AGENT-RUN HIERARCHY TEST")
    print("🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪")
    print()
    
    if not check_api_health():
        print("❌ API is not running!")
        print("   Start it with: python api.py")
        return
    
    print("✅ API is healthy")
    print()
    
    results = []
    
    # Test 1: Add run with user_id
    results.append(("Add Run with user_id", test_add_run_with_user()))
    
    # Test 2: Retrieve with user_id
    results.append(("Retrieve with user_id", test_retrieve_with_user()))
    
    # Test 3: Retrieve all with user_id
    results.append(("Retrieve All with user_id", test_retrieve_all_with_user()))
    
    # Test 4: Multiple users
    results.append(("Multiple Users", test_add_multiple_users()))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    for name, success in results:
        print(f"{'✅' if success else '❌'} {name}")
    
    all_passed = all(success for _, success in results)
    print("\n" + "="*70)
    if all_passed:
        print("✅ All tests passed!")
    else:
        print("⚠️  Some tests failed")


if __name__ == "__main__":
    main()

