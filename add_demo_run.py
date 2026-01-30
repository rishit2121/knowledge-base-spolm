"""Script to add a demo run for testing the Learnings page."""
import requests
import json
from datetime import datetime

# Use Vercel deployment URL (can be changed to localhost:8000 for local testing)
API_URL = "https://knowledge-base-spolm.vercel.app"
# API_URL = "http://localhost:8000"  # Uncomment for local testing


def add_demo_run():
    """Add a demo run with the specified agent_id and user_id."""
    print("="*70)
    print("Adding Demo Run")
    print("="*70)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Unique task to avoid similarity rejection
    unique_task = "Develop a comprehensive data analytics dashboard using React, D3.js, and Python Flask backend with real-time WebSocket updates for financial market monitoring and visualization"
    
    payload = {
        "run_id": f"demo_run_{timestamp}",
        "agent_id": "tI7St2M9woSSrj2zBGR5",
        "user_id": "spolmdemo@gmail.com",
        "user_task": unique_task,
        "status": "complete",
        "steps": [
            {
                "step_id": "step1",
                "step_name": "backend_setup",
                "step_type": "tool_call",
                "step_input": {"action": "Initialize Flask backend with REST API endpoints"},
                "step_output": {"data": "Backend server running on port 5000 with 5 API endpoints configured"}
            },
            {
                "step_id": "step2",
                "step_name": "frontend_development",
                "step_type": "tool_call",
                "step_input": {"action": "Build React dashboard with D3.js visualizations"},
                "step_output": {"data": "Frontend built with 3 interactive charts and real-time data feed"}
            },
            {
                "step_id": "step3",
                "step_name": "websocket_integration",
                "step_type": "llm_call",
                "step_input": {"protocol": "WebSocket", "use_case": "real-time market data"},
                "step_output": {"data": "WebSocket connection established, receiving updates every 100ms"}
            },
            {
                "step_id": "step4",
                "step_name": "data_processing",
                "step_type": "tool_call",
                "step_input": {"action": "Process and aggregate financial market data"},
                "step_output": {"data": "Processed 10,000+ data points, calculated moving averages and trends"}
            },
            {
                "step_id": "step5",
                "step_name": "deployment",
                "step_type": "tool_call",
                "step_input": {"platform": "Vercel + Railway"},
                "step_output": {"data": "Deployed to production, dashboard accessible at analytics.spolm.com"}
            }
        ],
        "final_output": "Data analytics dashboard successfully deployed with real-time financial market monitoring capabilities",
        "metadata": {
            "framework": "React + Flask",
            "visualization": "D3.js",
            "real_time": True,
            "domain": "financial_analytics",
            "complexity": "high"
        }
    }
    
    print(f"📝 Adding run:")
    print(f"   Run ID: {payload['run_id']}")
    print(f"   Agent ID: {payload['agent_id']}")
    print(f"   User ID: {payload['user_id']}")
    print(f"   Task: {unique_task[:80]}...")
    print()
    
    try:
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
            print("\n" + "="*70)
            print("✅ Run added successfully!")
            print("="*70)
            return True
        else:
            print(f"❌ Failed: {response.status_code}")
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


def check_api_health():
    """Check if API is running."""
    try:
        response = requests.get(f"{API_URL}/", timeout=5)
        return response.status_code == 200
    except:
        return False


if __name__ == "__main__":
    print("🚀 Adding Demo Run for Learnings Page")
    print()
    
    if not check_api_health():
        print(f"❌ API is not accessible at {API_URL}")
        print("   Make sure the API is running or check the URL")
        exit(1)
    
    print(f"✅ API is healthy at {API_URL}")
    print()
    
    success = add_demo_run()
    
    if success:
        print("\n✅ Demo run added successfully!")
        print("   You can now view it in the Learnings page")
    else:
        print("\n❌ Failed to add demo run")
        exit(1)
