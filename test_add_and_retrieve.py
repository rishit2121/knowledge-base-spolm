"""Simple test: Add a run, then retrieve it with a similar task using the API."""
import requests
import json
from datetime import datetime


def add_run(api_url="http://localhost:8000"):
    """Add a test run to the knowledge base using the API."""
    print("=" * 70)
    print("STEP 1: Adding a Run to Knowledge Base via API")
    print("=" * 70)
    
    # Your actual Gmail run log (as dict for API)
    payload = {
        "id": "sk_bf2482021dec13807eb41be0fcd2935b493b1d2950cf291eec9fe328c8c568cea81f4da7e0088c5d",
        "run_id": "e28b300f-406c-45d1-998e-46d365e1dd14",
        "start_timestamp": "2025-11-11T02:27:32.239Z",
        "agent_id": "GmailReadAndReply",
        "user_task": "Read the latest email and reply with 'chicken' in it",
        "metadata": {
            "agent_type": "Gmail AI Agent",
            "goal": "Read the latest email and reply with 'chicken' in it"
        },
        "steps": [
            {
                "step_id": "3c2a574b-ca03-44a4-ba72-d318e43f697d",
                "step_name": "reasoning",
                "step_type": "llm_call",
                "step_input": {
                    "goal": "Read the latest email and reply with 'chicken' in it",
                    "iteration": 1,
                    "context": {
                        "lastAction": "sendReply",
                        "lastResult": {
                            "success": True,
                            "message": "Reply sent successfully"
                        },
                        "emailData": {
                            "id": "19a70bb4236dd16c",
                            "threadId": "19a70b02bca55e5d",
                            "snippet": "Subject: Re: Research\n\nHi [Original Author Name],\n\nThanks so much for thinking of me and pointing me towards Shuxin's research opportunity at the PAIR Lab. It sounds like a great fit! I'm definitely going to look into it further and send my updated CV as suggested. Hopefully they are not too busy eating chicken and can take a look quickly. I appreciate your encouragement and will let you know how it goes.\n\nBest,\n\nSriram\n",
                            "from": "srimans572@gmail.com",
                            "subject": "Re: Research",
                            "messageId": "<CAA4URHbFj0paefohcK+9PQ50h8CMwsRtdJdR7Z1e4gcnvy9iqg@mail.gmail.com>"
                        },
                        "summary": "Sriram is grateful to the original author for recommending Shuxin's research opportunity at the PAIR Lab and intends to apply. He plans to send his updated CV and will update the original author on his progress.\n",
                        "reply": "Subject: Re: Research\n\nHi Sriram,\n\nGreat to hear you're planning to apply to Shuxin's PAIR Lab opportunity! I'm glad you found my recommendation helpful.\n\nDefinitely send your updated CV. Let me know how it goes – I'm rooting for you. Maybe one day you can tell me all about your research over some fried chicken!\n\nBest,\n\n[Your Name]\n"
                    }
                },
                "step_output": {
                    "action": "authenticate",
                    "reasoning": "The agent is not authenticated, so it needs to authenticate first."
                },
                "step_error": None,
                "step_end_time": "2025-11-11T02:27:32.996Z",
                "step_latency": 756,
                "tool_provider": "gemini",
                "options": {},
                "step_status": "success"
            },
            {
                "step_id": "9e5d0fec-95d7-4784-83f3-4c16ee87ce51",
                "step_name": "authenticate",
                "step_type": "auth_call",
                "step_input": [],
                "step_output": {"success": True},
                "step_error": None,
                "step_end_time": "2025-11-11T02:27:32.998Z",
                "step_latency": 2,
                "tool_provider": "gmail_oauth",
                "options": {},
                "step_status": "success"
            },
            {
                "step_id": "12916956-bdd2-473a-a72d-028501b1975f",
                "step_name": "reasoning",
                "step_type": "llm_call",
                "step_input": {
                    "goal": "Read the latest email and reply with 'chicken' in it",
                    "iteration": 2,
                    "context": {
                        "lastAction": "sendReply",
                        "lastResult": {
                            "success": True,
                            "message": "Reply sent successfully"
                        },
                        "emailData": {
                            "id": "19a70bb4236dd16c",
                            "threadId": "19a70b02bca55e5d",
                            "snippet": "Subject: Re: Research\n\nHi [Original Author Name],\n\nThanks so much for thinking of me and pointing me towards Shuxin's research opportunity at the PAIR Lab. It sounds like a great fit! I'm definitely going to look into it further and send my updated CV as suggested. Hopefully they are not too busy eating chicken and can take a look quickly. I appreciate your encouragement and will let you know how it goes.\n\nBest,\n\nSriram\n",
                            "from": "srimans572@gmail.com",
                            "subject": "Re: Research",
                            "messageId": "<CAA4URHbFj0paefohcK+9PQ50h8CMwsRtdJdR7Z1e4gcnvy9iqg@mail.gmail.com>"
                        },
                        "summary": "Sriram is grateful to the original author for recommending Shuxin's research opportunity at the PAIR Lab and intends to apply. He plans to send his updated CV and will update the original author on his progress.\n",
                        "reply": "Subject: Re: Research\n\nHi Sriram,\n\nGreat to hear you're planning to apply to Shuxin's PAIR Lab opportunity! I'm glad you found my recommendation helpful.\n\nDefinitely send your updated CV. Let me know how it goes – I'm rooting for you. Maybe one day you can tell me all about your research over some fried chicken!\n\nBest,\n\n[Your Name]\n"
                    }
                },
                "step_output": {
                    "action": "getLatestEmail",
                    "reasoning": "The agent is authenticated but has not retrieved an email yet."
                },
                "step_error": None,
                "step_end_time": "2025-11-11T02:27:33.562Z",
                "step_latency": 563,
                "tool_provider": "gemini",
                "options": {},
                "step_status": "success"
            },
            {
                "step_id": "d205156f-9391-4f51-b3d8-4ab4f67e5346",
                "step_name": "fetch_email",
                "step_type": "email",
                "step_input": [],
                "step_output": {
                    "success": True,
                    "data": {
                        "id": "19a70bb4236dd16c",
                        "threadId": "19a70b02bca55e5d",
                        "snippet": "Subject: Re: Research\n\nHi [Original Author Name],\n\nThanks so much for thinking of me and pointing me towards Shuxin's research opportunity at the PAIR Lab. It sounds like a great fit! I'm definitely going to look into it further and send my updated CV as suggested. Hopefully they are not too busy eating chicken and can take a look quickly. I appreciate your encouragement and will let you know how it goes.\n\nBest,\n\nSriram\n",
                        "from": "srimans572@gmail.com",
                        "subject": "Re: Research",
                        "messageId": "<CAA4URHbFj0paefohcK+9PQ50h8CMwsRtdJdR7Z1e4gcnvy9iqg@mail.gmail.com>"
                    }
                },
                "step_error": None,
                "step_end_time": "2025-11-11T02:27:33.855Z",
                "step_latency": 292,
                "tool_provider": "gmail",
                "options": {},
                "step_status": "success"
            },
            {
                "step_id": "c7ae05d2-7100-4813-a482-539c43242ee9",
                "step_name": "reasoning",
                "step_type": "llm_call",
                "step_input": {
                    "goal": "Read the latest email and reply with 'chicken' in it",
                    "iteration": 3,
                    "context": {
                        "lastAction": "sendReply",
                        "lastResult": {
                            "success": True,
                            "message": "Reply sent successfully"
                        },
                        "emailData": {
                            "id": "19a70bb4236dd16c",
                            "threadId": "19a70b02bca55e5d",
                            "snippet": "Subject: Re: Research\n\nHi [Original Author Name],\n\nThanks so much for thinking of me and pointing me towards Shuxin's research opportunity at the PAIR Lab. It sounds like a great fit! I'm definitely going to look into it further and send my updated CV as suggested. Hopefully they are not too busy eating chicken and can take a look quickly. I appreciate your encouragement and will let you know how it goes.\n\nBest,\n\nSriram\n",
                            "from": "srimans572@gmail.com",
                            "subject": "Re: Research",
                            "messageId": "<CAA4URHbFj0paefohcK+9PQ50h8CMwsRtdJdR7Z1e4gcnvy9iqg@mail.gmail.com>"
                        },
                        "summary": "Sriram is grateful to the original author for recommending Shuxin's research opportunity at the PAIR Lab and intends to apply. He plans to send his updated CV and will update the original author on his progress.\n",
                        "reply": "Subject: Re: Research\n\nHi Sriram,\n\nGreat to hear you're planning to apply to Shuxin's PAIR Lab opportunity! I'm glad you found my recommendation helpful.\n\nDefinitely send your updated CV. Let me know how it goes – I'm rooting for you. Maybe one day you can tell me all about your research over some fried chicken!\n\nBest,\n\n[Your Name]\n"
                    }
                },
                "step_output": {
                    "action": "summarizeEmail",
                    "reasoning": "We have an email but no summary yet, so we need to summarize the email."
                },
                "step_error": None,
                "step_end_time": "2025-11-11T02:27:34.631Z",
                "step_latency": 776,
                "tool_provider": "gemini",
                "options": {},
                "step_status": "success"
            },
            {
                "step_id": "aa0e9a2a-7ccf-4de4-902c-5a3ad8333f9e",
                "step_name": "summarize",
                "step_type": "llm_call",
                "step_input": "Subject: Re: Research\n\nHi [Original Author Name],\n\nThanks so much for thinking of me and pointing me towards Shuxin's research opportunity at the PAIR Lab. It sounds like a great fit! I'm definitely going to look into it further and send my updated CV as suggested. Hopefully they are not too busy eating chicken and can take a look quickly. I appreciate your encouragement and will let you know how it goes.\n\nBest,\n\nSriram\n",
                "step_output": {
                    "success": True,
                    "data": "Sriram is grateful to the original author for recommending Shuxin's research opportunity at the PAIR Lab and intends to apply. He plans to send his updated CV and will update the original author on his progress.\n"
                },
                "step_error": None,
                "step_end_time": "2025-11-11T02:27:35.394Z",
                "step_latency": 763,
                "tool_provider": "gemini",
                "options": {},
                "step_status": "success"
            },
            {
                "step_id": "5f1f8fad-2f8a-463f-aead-920a3fa255ac",
                "step_name": "reasoning",
                "step_type": "llm_call",
                "step_input": {
                    "goal": "Read the latest email and reply with 'chicken' in it",
                    "iteration": 4,
                    "context": {
                        "lastAction": "sendReply",
                        "lastResult": {
                            "success": True,
                            "message": "Reply sent successfully"
                        },
                        "emailData": {
                            "id": "19a70bb4236dd16c",
                            "threadId": "19a70b02bca55e5d",
                            "snippet": "Subject: Re: Research\n\nHi [Original Author Name],\n\nThanks so much for thinking of me and pointing me towards Shuxin's research opportunity at the PAIR Lab. It sounds like a great fit! I'm definitely going to look into it further and send my updated CV as suggested. Hopefully they are not too busy eating chicken and can take a look quickly. I appreciate your encouragement and will let you know how it goes.\n\nBest,\n\nSriram\n",
                            "from": "srimans572@gmail.com",
                            "subject": "Re: Research",
                            "messageId": "<CAA4URHbFj0paefohcK+9PQ50h8CMwsRtdJdR7Z1e4gcnvy9iqg@mail.gmail.com>"
                        },
                        "summary": "Sriram is grateful to the original author for recommending Shuxin's research opportunity at the PAIR Lab and intends to apply. He plans to send his updated CV and will update the original author on his progress.\n",
                        "reply": "Subject: Re: Research\n\nHi Sriram,\n\nGreat to hear you're planning to apply to Shuxin's PAIR Lab opportunity! I'm glad you found my recommendation helpful.\n\nDefinitely send your updated CV. Let me know how it goes – I'm rooting for you. Maybe one day you can tell me all about your research over some fried chicken!\n\nBest,\n\n[Your Name]\n"
                    }
                },
                "step_output": {
                    "action": "generateReply",
                    "reasoning": "We have an email, a summary, and haven't generated a reply yet."
                },
                "step_error": None,
                "step_end_time": "2025-11-11T02:27:36.170Z",
                "step_latency": 776,
                "tool_provider": "gemini",
                "options": {},
                "step_status": "success"
            },
            {
                "step_id": "5151a96d-e6a8-4e03-9d08-b00e091a6e45",
                "step_name": "generateReply",
                "step_type": "llm_call",
                "step_input": [
                    "Sriram is grateful to the original author for recommending Shuxin's research opportunity at the PAIR Lab and intends to apply. He plans to send his updated CV and will update the original author on his progress.\n",
                    "Re: Research"
                ],
                "step_output": {
                    "success": True,
                    "data": "Subject: Re: Research\n\nHi Sriram,\n\nGreat to hear you're planning to apply to Shuxin's PAIR Lab opportunity! I'm glad you found my recommendation helpful.\n\nDefinitely send your updated CV. Let me know how it goes – I'm rooting for you. Maybe one day you can tell me all about your research over some fried chicken!\n\nBest,\n\n[Your Name]\n"
                },
                "step_error": None,
                "step_end_time": "2025-11-11T02:27:37.232Z",
                "step_latency": 1062,
                "tool_provider": "gemini",
                "options": {},
                "step_status": "success"
            },
            {
                "step_id": "d4b9429b-a565-4ecf-b00d-63811fe8380e",
                "step_name": "reasoning",
                "step_type": "llm_call",
                "step_input": {
                    "goal": "Read the latest email and reply with 'chicken' in it",
                    "iteration": 5,
                    "context": {
                        "lastAction": "sendReply",
                        "lastResult": {
                            "success": True,
                            "message": "Reply sent successfully"
                        },
                        "emailData": {
                            "id": "19a70bb4236dd16c",
                            "threadId": "19a70b02bca55e5d",
                            "snippet": "Subject: Re: Research\n\nHi [Original Author Name],\n\nThanks so much for thinking of me and pointing me towards Shuxin's research opportunity at the PAIR Lab. It sounds like a great fit! I'm definitely going to look into it further and send my updated CV as suggested. Hopefully they are not too busy eating chicken and can take a look quickly. I appreciate your encouragement and will let you know how it goes.\n\nBest,\n\nSriram\n",
                            "from": "srimans572@gmail.com",
                            "subject": "Re: Research",
                            "messageId": "<CAA4URHbFj0paefohcK+9PQ50h8CMwsRtdJdR7Z1e4gcnvy9iqg@mail.gmail.com>"
                        },
                        "summary": "Sriram is grateful to the original author for recommending Shuxin's research opportunity at the PAIR Lab and intends to apply. He plans to send his updated CV and will update the original author on his progress.\n",
                        "reply": "Subject: Re: Research\n\nHi Sriram,\n\nGreat to hear you're planning to apply to Shuxin's PAIR Lab opportunity! I'm glad you found my recommendation helpful.\n\nDefinitely send your updated CV. Let me know how it goes – I'm rooting for you. Maybe one day you can tell me all about your research over some fried chicken!\n\nBest,\n\n[Your Name]\n"
                    }
                },
                "step_output": {
                    "action": "sendReply",
                    "reasoning": "We have an email, a summary, and a generated reply, but the reply hasn't been sent yet."
                },
                "step_error": None,
                "step_end_time": "2025-11-11T02:27:38.161Z",
                "step_latency": 927,
                "tool_provider": "gemini",
                "options": {},
                "step_status": "success"
            },
            {
                "step_id": "37855ed2-7395-4cb9-8b0f-2c01bdeb2443",
                "step_name": "sendReply",
                "step_type": "email",
                "step_input": [
                    "Subject: Re: Research\n\nHi Sriram,\n\nGreat to hear you're planning to apply to Shuxin's PAIR Lab opportunity! I'm glad you found my recommendation helpful.\n\nDefinitely send your updated CV. Let me know how it goes – I'm rooting for you. Maybe one day you can tell me all about your research over some fried chicken!\n\nBest,\n\n[Your Name]\n",
                    {
                        "id": "19a70bb4236dd16c",
                        "threadId": "19a70b02bca55e5d",
                        "snippet": "Subject: Re: Research\n\nHi [Original Author Name],\n\nThanks so much for thinking of me and pointing me towards Shuxin's research opportunity at the PAIR Lab. It sounds like a great fit! I'm definitely going to look into it further and send my updated CV as suggested. Hopefully they are not too busy eating chicken and can take a look quickly. I appreciate your encouragement and will let you know how it goes.\n\nBest,\n\nSriram\n",
                        "from": "srimans572@gmail.com",
                        "subject": "Re: Research",
                        "messageId": "<CAA4URHbFj0paefohcK+9PQ50h8CMwsRtdJdR7Z1e4gcnvy9iqg@mail.gmail.com>"
                    }
                ],
                "step_output": {"success": True, "message": "Reply sent successfully"},
                "step_error": None,
                "step_end_time": "2025-11-11T02:27:38.720Z",
                "step_latency": 524,
                "tool_provider": "gmail",
                "options": {},
                "step_status": "success"
            },
            {
                "step_id": "775da5fc-b47c-4ac2-b1bc-8e7471197d3f",
                "step_name": "reasoning",
                "step_type": "llm_call",
                "step_input": {
                    "goal": "Read the latest email and reply with 'chicken' in it",
                    "iteration": 6,
                    "context": {
                        "lastAction": "sendReply",
                        "lastResult": {
                            "success": True,
                            "message": "Reply sent successfully"
                        },
                        "emailData": {
                            "id": "19a70bb4236dd16c",
                            "threadId": "19a70b02bca55e5d",
                            "snippet": "Subject: Re: Research\n\nHi [Original Author Name],\n\nThanks so much for thinking of me and pointing me towards Shuxin's research opportunity at the PAIR Lab. It sounds like a great fit! I'm definitely going to look into it further and send my updated CV as suggested. Hopefully they are not too busy eating chicken and can take a look quickly. I appreciate your encouragement and will let you know how it goes.\n\nBest,\n\nSriram\n",
                            "from": "srimans572@gmail.com",
                            "subject": "Re: Research",
                            "messageId": "<CAA4URHbFj0paefohcK+9PQ50h8CMwsRtdJdR7Z1e4gcnvy9iqg@mail.gmail.com>"
                        },
                        "summary": "Sriram is grateful to the original author for recommending Shuxin's research opportunity at the PAIR Lab and intends to apply. He plans to send his updated CV and will update the original author on his progress.\n",
                        "reply": "Subject: Re: Research\n\nHi Sriram,\n\nGreat to hear you're planning to apply to Shuxin's PAIR Lab opportunity! I'm glad you found my recommendation helpful.\n\nDefinitely send your updated CV. Let me know how it goes – I'm rooting for you. Maybe one day you can tell me all about your research over some fried chicken!\n\nBest,\n\n[Your Name]\n"
                    }
                },
                "step_output": {
                    "action": "complete",
                    "reasoning": "The email has been received, summarized, replied to, and sent successfully."
                },
                "step_error": None,
                "step_end_time": "2025-11-11T02:27:39.384Z",
                "step_latency": 664,
                "tool_provider": "gemini",
                "options": {},
                "step_status": "success"
            }
        ],
        "final_output": "Completed successfully",
        "duration": 7147,
        "status": "complete",
        "agent_prompt": "Gmail automation agent that reads latest email and replies with 'chicken' in the response",
        "end_timestamp": "2025-11-11T02:27:39.386Z"
    }
    
    print(f"\n📝 Adding run via API:")
    print(f"   Task: {payload['user_task']}")
    print(f"   Run ID: {payload['run_id']}")
    print(f"   Status: {payload['status']}")
    print(f"   Steps: {len(payload['steps']) if payload.get('steps') else 0}")
    print(f"   API URL: {api_url}/runs")
    
    try:
        response = requests.post(
            f"{api_url}/runs",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        result = response.json()
        
        if result.get("status") == "success":
            print(f"\n✅ Run added successfully via API!")
            data = result.get("data", {})
            print(f"   Task ID: {data.get('task_id')}")
            print(f"   References: {data.get('references_count')}")
            print(f"   Artifacts: {data.get('artifacts_count')}")
            return payload['run_id']
        else:
            print(f"\n❌ Failed to add run: {result.get('detail', 'Unknown error')}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"\n❌ API request failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"   Response: {e.response.text}")
        return None


def retrieve_similar(run_id: str, api_url="http://localhost:8000"):
    """Retrieve the run using a similar but not exact task via API."""
    print("\n" + "=" * 70)
    print("STEP 2: Retrieving with Similar Task via API")
    print("=" * 70)
    
    # Use a similar but not exact task
    # Original: "Read the latest email and reply with 'chicken' in it"
    # Similar: "I need to read an email and send a reply"
    request_payload = {
        "task_text": "I need to read an email and send a reply",
        "agent_id": "GmailReadAndReply",
        "top_k": 5
    }
    
    print(f"\n🔍 Searching via API:")
    print(f"   Query: '{request_payload['task_text']}'")
    print(f"   (Original task was: 'Read the latest email and reply with 'chicken' in it')")
    print(f"   Top K: {request_payload['top_k']}")
    print(f"   API URL: {api_url}/retrieve")
    
    try:
        response = requests.post(
            f"{api_url}/retrieve",
            json=request_payload,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        result = response.json()
        
        print(f"\n✅ Retrieval complete via API!")
        print(f"   Confidence: {result.get('confidence', 0):.2%}")
        
        print(f"\n📊 Observations:")
        for i, obs in enumerate(result.get('observations', []), 1):
            print(f"   {i}. {obs}")
        
        related_runs = result.get('related_runs', [])
        print(f"\n📚 Found {len(related_runs)} related run(s):")
        
        found_our_run = False
        for i, run in enumerate(related_runs, 1):
            is_our_run = run.get('run_id') == run_id
            if is_our_run:
                found_our_run = True
            
            print(f"\n   Run {i}:")
            print(f"   - ID: {run.get('run_id')} {'⭐ (This is the run we just added!)' if is_our_run else ''}")
            print(f"   - Similarity: {run.get('similarity_score', 0):.3f}")
            print(f"   - Outcome: {run.get('outcome')}")
            print(f"   - Summary: {run.get('summary', '')[:150]}...")
            print(f"   - References: {len(run.get('references', []))}")
            print(f"   - Artifacts: {len(run.get('artifacts', []))}")
            if run.get('run_tree'):
                print(f"   - Has full run_tree: ✅")
                run_tree = run.get('run_tree', {})
                if isinstance(run_tree, dict):
                    print(f"   - Run tree keys: {list(run_tree.keys())[:5]}...")
            else:
                print(f"   - Has full run_tree: ❌")
        
        if found_our_run:
            print(f"\n🎉 SUCCESS! The run we just added was retrieved via API!")
            print(f"   The semantic search found it even though the query was slightly different.")
        else:
            print(f"\n⚠️  The run we added wasn't in the top results.")
            print(f"   This might mean similarity was below threshold or there are many similar runs.")
        
        return result
    except requests.exceptions.RequestException as e:
        print(f"\n❌ API request failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"   Response: {e.response.text}")
        return None


if __name__ == "__main__":
    import sys
    
    print("\n" + "🧪 " * 35)
    print("ADD AND RETRIEVE TEST (via API)")
    print("🧪 " * 35 + "\n")
    
    # Get API URL from command line or use default
    api_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    
    print(f"🌐 Using API: {api_url}")
    print(f"   Make sure the API server is running: python api.py")
    print()
    
    # Check if API is running
    try:
        health_check = requests.get(f"{api_url}/", timeout=2)
        if health_check.status_code == 200:
            print("✅ API server is running\n")
        else:
            print("⚠️  API server responded but may not be ready\n")
    except requests.exceptions.RequestException:
        print("⚠️  Could not connect to API server")
        print(f"   Make sure it's running at {api_url}")
        print(f"   Start it with: python api.py\n")
        sys.exit(1)
    
    # Step 1: Add a run via API
    run_id = add_run(api_url)
    
    if run_id:
        # Step 2: Retrieve it with a similar task via API
        retrieve_similar(run_id, api_url)
        
        print("\n" + "=" * 70)
        print("✅ TEST COMPLETE")
        print("=" * 70)
    else:
        print("\n❌ Could not add run, skipping retrieval test")

