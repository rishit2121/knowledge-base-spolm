"""Test script for the Decision Layer."""
import requests
import json
from datetime import datetime

# API URL (change if needed)
API_URL = "http://localhost:8000"  # Local
# API_URL = "https://knowledge-base-spolm.vercel.app"  # Vercel

def test_add_decision():
    """Test ADD decision - new unique run."""
    print("\n" + "="*60)
    print("TEST 1: ADD Decision (New Unique Run)")
    print("="*60)
    
    payload = {
        "run_id": f"test_add_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "agent_id": "test_agent",
        "user_task": "Create a completely new database schema for user authentication",
        "status": "complete",
        "steps": [
            {
                "step_id": "step1",
                "step_name": "design_schema",
                "step_type": "tool_call",
                "step_output": {"data": "Created schema with users, sessions, tokens"}
            }
        ]
    }
    
    response = requests.post(f"{API_URL}/runs", json=payload)
    print(f"Status: {response.status_code}")
    if response.status_code != 200:
        print(f"❌ Error Response: {response.text[:500]}")
        try:
            error_detail = response.json()
            print(f"Error Detail: {error_detail.get('detail', 'Unknown error')[:500]}")
        except:
            pass
        return None
    result = response.json()
    data = result.get('data', result)
    print(f"Decision: {data.get('decision', 'N/A')}")
    print(f"Reason: {data.get('reason', 'N/A')}")
    
    return data.get("run_id")


def test_not_decision(existing_run_id=None):
    """Test NOT decision - redundant run."""
    print("\n" + "="*60)
    print("TEST 2: NOT Decision (Redundant Run)")
    print("="*60)
    
    # Use same task as previous run
    payload = {
        "run_id": f"test_not_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "agent_id": "test_agent",
        "user_task": "Create a completely new database schema for user authentication",  # Same task
        "status": "complete",
        "steps": [
            {
                "step_id": "step1",
                "step_name": "design_schema",
                "step_type": "tool_call",
                "step_output": {"data": "Created schema with users, sessions, tokens"}  # Same output
            }
        ]
    }
    
    response = requests.post(f"{API_URL}/runs", json=payload)
    print(f"Status: {response.status_code}")
    if response.status_code != 200:
        print(f"❌ Error Response: {response.text[:500]}")
        try:
            error_detail = response.json()
            print(f"Error Detail: {error_detail.get('detail', 'Unknown error')[:500]}")
        except:
            pass
        return
    result = response.json()
    data = result.get('data', result)
    print(f"Decision: {data.get('decision', 'N/A')}")
    print(f"Reason: {data.get('reason', 'N/A')}")
    
    if data.get("decision") == "NOT":
        print("✅ Correctly identified as redundant!")
    else:
        print("⚠️  Expected NOT, got different decision")


def test_replace_decision():
    """Test REPLACE decision - better version."""
    print("\n" + "="*60)
    print("TEST 3: REPLACE Decision (Better Version)")
    print("="*60)
    
    # First, create a failed run
    failed_payload = {
        "run_id": f"test_replace_failed_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "agent_id": "test_agent",
        "user_task": "Generate optimized SQL queries for user data",
        "status": "failure",
        "steps": [
            {
                "step_id": "step1",
                "step_name": "generate_query",
                "step_type": "tool_call",
                "step_output": {"data": "SELECT * FROM users"}  # Inefficient
            }
        ]
    }
    
    print("Creating failed run...")
    response = requests.post(f"{API_URL}/runs", json=failed_payload)
    failed_result = response.json()
    failed_run_id = failed_result.get("run_id")
    print(f"Failed run ID: {failed_run_id}")
    
    # Now create a successful run with same task
    success_payload = {
        "run_id": f"test_replace_success_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "agent_id": "test_agent",
        "user_task": "Generate optimized SQL queries for user data",  # Same task
        "status": "complete",  # Success!
        "steps": [
            {
                "step_id": "step1",
                "step_name": "generate_query",
                "step_type": "tool_call",
                "step_output": {"data": "SELECT id, name, email FROM users WHERE active = true"}  # Optimized
            }
        ]
    }
    
    print("\nCreating successful run (should REPLACE failed one)...")
    response = requests.post(f"{API_URL}/runs", json=success_payload)
    print(f"Status: {response.status_code}")
    if response.status_code != 200:
        print(f"❌ Error Response: {response.text[:500]}")
        try:
            error_detail = response.json()
            print(f"Error Detail: {error_detail.get('detail', 'Unknown error')[:500]}")
        except:
            pass
        return
    result = response.json()
    data = result.get('data', result)
    print(f"Decision: {data.get('decision', 'N/A')}")
    print(f"Target Run ID: {data.get('target_run_id', 'N/A')}")
    print(f"Reason: {data.get('reason', 'N/A')}")
    
    if data.get("decision") == "REPLACE":
        print("✅ Correctly identified as replacement!")
    else:
        print("⚠️  Expected REPLACE, got different decision")


def test_merge_decision():
    """Test MERGE decision - complementary runs."""
    print("\n" + "="*60)
    print("TEST 4: MERGE Decision (Complementary Runs)")
    print("="*60)
    
    # First run with approach A
    run1_payload = {
        "run_id": f"test_merge_1_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "agent_id": "test_agent",
        "user_task": "Build REST API for user management",
        "status": "complete",
        "steps": [
            {
                "step_id": "step1",
                "step_name": "design_api",
                "step_type": "tool_call",
                "step_output": {"data": "Designed REST endpoints using Flask"}
            }
        ]
    }
    
    print("Creating first run (approach A)...")
    response = requests.post(f"{API_URL}/runs", json=run1_payload)
    if response.status_code != 200:
        print(f"❌ Error creating first run: {response.text[:500]}")
        return
    run1_result = response.json()
    data1 = run1_result.get('data', run1_result)
    run1_id = data1.get("run_id")
    print(f"Run 1 ID: {run1_id}")
    
    # Second run with approach B (complementary)
    run2_payload = {
        "run_id": f"test_merge_2_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "agent_id": "test_agent",
        "user_task": "Build REST API for user management",  # Same task
        "status": "complete",
        "steps": [
            {
                "step_id": "step1",
                "step_name": "design_api",
                "step_type": "tool_call",
                "step_output": {"data": "Designed REST endpoints using FastAPI"}  # Different approach
            }
        ]
    }
    
    print("\nCreating second run (approach B, should MERGE)...")
    response = requests.post(f"{API_URL}/runs", json=run2_payload)
    print(f"Status: {response.status_code}")
    if response.status_code != 200:
        print(f"❌ Error Response: {response.text[:500]}")
        try:
            error_detail = response.json()
            print(f"Error Detail: {error_detail.get('detail', 'Unknown error')[:500]}")
        except:
            pass
        return
    result = response.json()
    data = result.get('data', result)
    print(f"Decision: {data.get('decision', 'N/A')}")
    print(f"Target Run ID: {data.get('target_run_id', 'N/A')}")
    print(f"Reason: {data.get('reason', 'N/A')}")
    
    if data.get("decision") == "MERGE":
        print("✅ Correctly identified as complementary!")
    else:
        print("⚠️  Expected MERGE, got different decision")


def check_stats():
    """Check knowledge base statistics."""
    print("\n" + "="*60)
    print("KNOWLEDGE BASE STATISTICS")
    print("="*60)
    
    response = requests.get(f"{API_URL}/stats")
    if response.status_code == 200:
        stats = response.json()
        print(f"Tasks: {stats.get('task_count', 0)}")
        print(f"Runs: {stats.get('run_count', 0)}")
        print(f"References: {stats.get('reference_count', 0)}")
        print(f"Artifacts: {stats.get('artifact_count', 0)}")
    else:
        print(f"Error: {response.status_code}")


if __name__ == "__main__":
    print("\n" + "🧪" * 20)
    print("DECISION LAYER TEST SUITE")
    print("🧪" * 20)
    
    # Check API health
    try:
        response = requests.get(f"{API_URL}/")
        if response.status_code != 200:
            print(f"❌ API not healthy. Status: {response.status_code}")
            exit(1)
        print("✅ API is healthy")
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        print(f"   Make sure the API is running at {API_URL}")
        exit(1)
    
    # Run tests
    try:
        # Test 1: ADD
        run_id = test_add_decision()
        
        # Test 2: NOT (redundant)
        test_not_decision(run_id)
        
        # Test 3: REPLACE
        test_replace_decision()
        
        # Test 4: MERGE
        test_merge_decision()
        
        # Check stats
        check_stats()
        
        print("\n" + "="*60)
        print("✅ All tests completed!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

