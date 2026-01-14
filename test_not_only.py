"""Test ONLY the NOT decision - assumes a run already exists."""
import requests
import json
from datetime import datetime
import time

# API URL - localhost for local testing
API_URL = "http://localhost:8000"


def test_not_decision_only():
    """
    Test that redundant runs are rejected (NOT decision).
    
    This assumes a similar run already exists in the database.
    It will try to add the same run again (should be NOT).
    """
    print("\n" + "="*70)
    print("TEST: NOT Decision - Redundant Run Rejection")
    print("="*70)
    print(f"API URL: {API_URL}\n")
    
    # Add the same run again (should be NOT)
    print("📝 Adding redundant run (should be NOT)")
    print("-" * 70)
    
    # Use the exact same task and similar structure
    run_payload = {
        "run_id": f"test_not_redundant_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
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
        print(f"Sending request to {API_URL}/runs")
        print(f"Payload task: {run_payload['user_task']}")
        response = requests.post(f"{API_URL}/runs", json=run_payload, timeout=30)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            data = result.get('data', result)
            decision = data.get('decision', 'N/A')
            reason = data.get('reason', 'N/A')
            message = result.get('message', 'N/A')
            
            print(f"\n✅ Run processed")
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
                print(f"   Check the SERVER CONSOLE for [DEBUG] messages")
                print(f"   showing the Gemini response")
                print("="*70)
                return False
        else:
            print(f"❌ Failed to process run")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text[:500]}")
            return False
            
    except Exception as e:
        print(f"❌ Error processing run: {e}")
        import traceback
        traceback.print_exc()
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
        print(f"   Make sure the API is running at {API_URL}")
        return False


if __name__ == "__main__":
    print("\n" + "🧪" * 35)
    print("NOT DECISION TEST ONLY - Localhost")
    print("🧪" * 35)
    print("\n⚠️  Make sure your API server is running:")
    print("   python api.py")
    print("   or")
    print("   uvicorn api:app --reload --port 8000")
    print()
    
    # Check API health
    if not check_api_health():
        print("\n❌ API is not accessible. Exiting.")
        exit(1)
    
    # Run test
    test_result = test_not_decision_only()
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"NOT Decision Test: {'✅ PASSED' if test_result else '❌ FAILED'}")
    print("="*70)
    
    if test_result:
        print("\n🎉 Test passed!")
        exit(0)
    else:
        print("\n⚠️  Test failed.")
        print("   Check the SERVER CONSOLE (where you ran 'python api.py')")
        print("   for [DEBUG] messages showing the Gemini response.")
        exit(1)

