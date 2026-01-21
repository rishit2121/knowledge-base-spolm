"""Test NOT decision - redundant run rejection using production API."""
import requests
import json
from datetime import datetime
import time

# API URL - Change to localhost for local testing
# API_URL = "http://localhost:8000"  # Local
API_URL = "https://knowledge-base-spolm.vercel.app"  # Production


def test_not_decision_only():
    """
    Test that redundant runs are rejected (NOT decision).
    
    This test assumes a run already exists in the database.
    It will try to add the same run again (should be NOT).
    """
    print("\n" + "="*70)
    print("TEST: NOT Decision - Redundant Run Rejection")
    print("="*70)
    print(f"API URL: {API_URL}\n")
    
    # Step 1: Add a run (this should already exist, but we'll add it to ensure it's there)
    print("📝 Step 1: Ensuring first run exists")
    print("-" * 70)
    
    first_run_payload = {
        "run_id": f"test_not_first_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "agent_id": "test_agent_not",
        "user_task": "Generate a comprehensive user authentication system with JWT tokens",
        "status": "complete",
        "steps": [
            {
                "step_id": "step1",
                "step_name": "design_auth",
                "step_type": "llm_call",
                "step_input": {
                    "goal": "Design authentication system"
                },
                "step_output": {
                    "data": "Designed JWT-based authentication with refresh tokens"
                }
            },
            {
                "step_id": "step2",
                "step_name": "implement_auth",
                "step_type": "tool_call",
                "step_output": {
                    "data": "Implemented authentication endpoints"
                }
            }
        ],
        "final_output": "Authentication system created successfully",
        "duration": 5000
    }
    
    try:
        response = requests.post(f"{API_URL}/runs", json=first_run_payload, timeout=30)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            data = result.get('data', result)
            decision = data.get('decision', 'N/A')
            reason = data.get('reason', 'N/A')
            run_id = data.get('run_id', 'N/A')
            
            print(f"✅ First run added successfully")
            print(f"   Decision: {decision}")
            print(f"   Run ID: {run_id}")
            print(f"   Reason: {reason}")
            
            if decision != "ADD":
                print(f"⚠️  Expected ADD, got {decision}")
                return False
            
            # Wait a bit to avoid rate limits
            print("\n⏳ Waiting 5 seconds to avoid rate limits...")
            time.sleep(5)
            
        else:
            print(f"❌ Failed to add first run")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text[:500]}")
            return False
            
    except Exception as e:
        print(f"❌ Error adding first run: {e}")
        return False
    
    # Step 2: Add the same run again (should be NOT)
    print("\n📝 Step 2: Adding same run again (should be NOT)")
    print("-" * 70)
    
    # Use the exact same task and similar structure
    second_run_payload = {
        "run_id": f"test_not_second_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "agent_id": "test_agent_not",
        "user_task": "Generate a comprehensive user authentication system with JWT tokens",  # Same task
        "status": "complete",
        "steps": [
            {
                "step_id": "step1",
                "step_name": "design_auth",
                "step_type": "llm_call",
                "step_input": {
                    "goal": "Design authentication system"
                },
                "step_output": {
                    "data": "Designed JWT-based authentication with refresh tokens"  # Same output
                }
            },
            {
                "step_id": "step2",
                "step_name": "implement_auth",
                "step_type": "tool_call",
                "step_output": {
                    "data": "Implemented authentication endpoints"  # Same output
                }
            }
        ],
        "final_output": "Authentication system created successfully",  # Same output
        "duration": 5000
    }
    
    try:
        response = requests.post(f"{API_URL}/runs", json=second_run_payload, timeout=30)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            data = result.get('data', result)
            decision = data.get('decision', 'N/A')
            reason = data.get('reason', 'N/A')
            message = result.get('message', 'N/A')
            
            print(f"✅ Second run processed")
            print(f"   Decision: {decision}")
            print(f"   Message: {message}")
            print(f"   Reason: {reason}")
            
            if decision == "NOT":
                print("\n" + "="*70)
                print("✅ SUCCESS: Redundant run correctly rejected (NOT decision)")
                print("="*70)
                return True
            else:
                print("\n" + "="*70)
                print(f"⚠️  Expected NOT decision, got {decision}")
                print("="*70)
                print(f"   This might mean:")
                print(f"   - Similarity threshold is too low")
                print(f"   - LLM judge decided it's different enough")
                print(f"   - Decision layer needs tuning")
                print("="*70)
                return False
        else:
            print(f"❌ Failed to process second run")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text[:500]}")
            return False
            
    except Exception as e:
        print(f"❌ Error processing second run: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_not_decision_with_slight_variation():
    """
    Test NOT decision with a slightly different but still redundant run.
    """
    print("\n" + "="*70)
    print("TEST: NOT Decision - Slightly Different but Redundant Run")
    print("="*70)
    print(f"API URL: {API_URL}\n")
    
    # Step 1: Add first run
    print("📝 Step 1: Adding first run")
    print("-" * 70)
    
    first_run_payload = {
        "run_id": f"test_not_variant_first_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "agent_id": "test_agent_not_variant",
        "user_task": "Create a REST API for managing user profiles",
        "status": "complete",
        "steps": [
            {
                "step_id": "step1",
                "step_name": "design_api",
                "step_type": "llm_call",
                "step_output": {
                    "data": "Designed REST API with CRUD operations"
                }
            }
        ]
    }
    
    try:
        response = requests.post(f"{API_URL}/runs", json=first_run_payload, timeout=30)
        if response.status_code != 200:
            print(f"❌ Failed to add first run: {response.status_code}")
            return False
        
        result = response.json()
        data = result.get('data', result)
        print(f"✅ First run added (Decision: {data.get('decision', 'N/A')})")
        
        # Wait to avoid rate limits
        print("\n⏳ Waiting 5 seconds...")
        time.sleep(5)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Step 2: Add very similar run (slightly different wording but same task)
    print("\n📝 Step 2: Adding very similar run (should be NOT)")
    print("-" * 70)
    
    second_run_payload = {
        "run_id": f"test_not_variant_second_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "agent_id": "test_agent_not_variant",
        "user_task": "Build a REST API for user profile management",  # Slightly different wording
        "status": "complete",
        "steps": [
            {
                "step_id": "step1",
                "step_name": "design_api",
                "step_type": "llm_call",
                "step_output": {
                    "data": "Designed REST API with CRUD operations"  # Same output
                }
            }
        ]
    }
    
    try:
        response = requests.post(f"{API_URL}/runs", json=second_run_payload, timeout=30)
        if response.status_code != 200:
            print(f"❌ Failed: {response.status_code}")
            return False
        
        result = response.json()
        data = result.get('data', result)
        decision = data.get('decision', 'N/A')
        reason = data.get('reason', 'N/A')
        
        print(f"Decision: {decision}")
        print(f"Reason: {reason}")
        
        if decision == "NOT":
            print("\n✅ SUCCESS: Similar run correctly rejected")
            return True
        else:
            print(f"\n⚠️  Got {decision} instead of NOT")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def check_api_health():
    """Check if API is accessible."""
    try:
        response = requests.get(f"{API_URL}/", timeout=10)
        if response.status_code == 200:
            print("✅ API is healthy")
            return True
        else:
            print(f"⚠️  API returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        print(f"   Make sure the API is deployed at {API_URL}")
        return False


if __name__ == "__main__":
    print("\n" + "🧪" * 35)
    print("NOT DECISION TEST - Production API")
    print("🧪" * 35)
    
    # Check API health
    if not check_api_health():
        print("\n❌ API is not accessible. Exiting.")
        exit(1)
    
    # Run tests
    print("\n")
    test1_result = test_not_decision()
    
    print("\n")
    time.sleep(10)  # Wait to avoid rate limits
    test2_result = test_not_decision_with_slight_variation()
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Test 1 (Exact duplicate): {'✅ PASSED' if test1_result else '❌ FAILED'}")
    print(f"Test 2 (Slight variation): {'✅ PASSED' if test2_result else '❌ FAILED'}")
    print("="*70)
    
    if test1_result and test2_result:
        print("\n🎉 All tests passed!")
        exit(0)
    else:
        print("\n⚠️  Some tests failed. Check the output above.")
        exit(1)

