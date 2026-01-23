"""Test script for the retrieve_all endpoint."""
import requests
import json
from typing import Dict, Any, Optional


def test_retrieve_all(
    api_url: str = "https://knowledge-base-spolm.vercel.app",
    agent_id: Optional[str] = None,
    limit: Optional[int] = None
):
    """
    Test the retrieve_all endpoint.
    
    Args:
        api_url: Base URL of the API
        agent_id: Optional agent ID filter
        limit: Optional limit on number of runs
    """
    print("="*70)
    print("TEST: Retrieve All Runs")
    print("="*70)
    print(f"API URL: {api_url}")
    
    if agent_id:
        print(f"Filtering by agent_id: {agent_id}")
    if limit:
        print(f"Limit: {limit}")
    print()
    
    # Build URL with query parameters
    url = f"{api_url}/retrieve_all"
    params = {}
    if agent_id:
        params["agent_id"] = agent_id
    if limit:
        params["limit"] = limit
    
    try:
        print(f"📡 Sending GET request to {url}")
        if params:
            print(f"   Query parameters: {params}")
        print()
        
        response = requests.get(url, params=params, timeout=30)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            runs = data.get("runs", [])
            total_count = data.get("total_count", 0)
            
            print(f"✅ Successfully retrieved {total_count} run(s)")
            print()
            print("="*70)
            print("RUNS SUMMARY")
            print("="*70)
            
            if not runs:
                print("No runs found in the knowledge base.")
            else:
                for i, run in enumerate(runs, 1):
                    print(f"\n[{i}] Run ID: {run.get('run_id', 'N/A')}")
                    print(f"    Agent ID: {run.get('agent_id', 'N/A')}")
                    print(f"    Summary: {run.get('summary', 'N/A')[:100]}...")
                    print(f"    Outcome: {run.get('outcome', 'N/A')}")
                    print(f"    Created At: {run.get('created_at', 'N/A')}")
                    print(f"    References: {len(run.get('references', []))}")
                    print(f"    Artifacts: {len(run.get('artifacts', []))}")
                    if run.get('run_tree'):
                        print(f"    Has Run Tree: Yes")
                    else:
                        print(f"    Has Run Tree: No")
            
            print()
            print("="*70)
            print("FULL JSON RESPONSE")
            print("="*70)
            print(json.dumps(data, indent=2, default=str))
            
            return True
        else:
            print(f"❌ Failed to retrieve runs")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def check_api_health(api_url: str) -> bool:
    """Check if the API is healthy."""
    try:
        response = requests.get(f"{api_url}/", timeout=5)
        return response.status_code == 200
    except:
        return False


def main():
    """Main test function."""
    print("🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪")
    print("RETRIEVE ALL ENDPOINT TEST")
    print("🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪")
    print()
    
    # Default to localhost, but can be changed
    api_url = "http://localhost:8000"
    
    # Check if user wants to test Vercel deployment
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == "--vercel" or sys.argv[1] == "--prod":
            api_url = "https://knowledge-base-spolm.vercel.app"
            print("🌐 Testing Vercel deployment")
        elif sys.argv[1].startswith("http"):
            api_url = sys.argv[1]
            print(f"🌐 Testing custom URL: {api_url}")
        else:
            print(f"⚠️  Unknown argument: {sys.argv[1]}")
            print("   Usage: python test_retrieve_all.py [--vercel|--prod|<url>]")
            return
    else:
        print("⚠️  Make sure your API server is running:")
        print("   python api.py")
        print("   or")
        print("   uvicorn api:app --reload --port 8000")
        print()
    
    # Check API health
    if not check_api_health(api_url):
        print(f"❌ API is not healthy at {api_url}")
        print("   Make sure the server is running and accessible.")
        return
    
    print("✅ API is healthy")
    print()
    
    # Test 1: Retrieve all runs
    print("\n" + "="*70)
    print("TEST 1: Retrieve All Runs (No Filters)")
    print("="*70)
    # success1 = test_retrieve_all(api_url=api_url)
    
    # Test 2: Retrieve with limit
    print("\n" + "="*70)
    print("TEST 2: Retrieve All Runs (Limit: 5)")
    print("="*70)
    # success2 = test_retrieve_all(api_url=api_url, limit=5)
    
    # Test 3: Retrieve with agent_id filter (if we have agent IDs)
    # This will only work if there are runs with agent_id set
    print("\n" + "="*70)
    print("TEST 3: Retrieve All Runs (Agent ID Filter - Optional)")
    print("="*70)
    print("Note: This test will only work if you have runs with agent_id set.")
    print("Skipping this test by default. Uncomment to test with a specific agent_id.")
    success3 = test_retrieve_all(api_url=api_url, agent_id="test_agent_001")
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    
    # if success1 and success2:
    #     print("\n✅ All tests passed!")
    # else:
    #     print("\n⚠️  Some tests failed. Check the output above for details.")


if __name__ == "__main__":
    main()

