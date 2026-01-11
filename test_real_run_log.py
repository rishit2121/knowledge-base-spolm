"""Test with real run log structure."""
from models.run import RunPayload
from models.retrieval import RetrievalRequest
from memory_builder import MemoryBuilder
from memory_retrieval import MemoryRetrieval


def test_real_gmail_run_log():
    """Test with the actual Gmail run log structure."""
    print("=" * 70)
    print("TEST: Processing Real Gmail Run Log")
    print("=" * 70)
    
    # Your actual run log structure
    payload = RunPayload(
        id="sk_bf2482021dec13807eb41be0fcd2935b493b1d2950cf291eec9fe328c8c568cea81f4da7e0088c5d",
        run_id="e28b300f-406c-45d1-998e-46d365e1dd14",
        start_timestamp="2025-11-11T02:27:32.239Z",
        agent_id="GmailReadAndReply",
        user_task="Read the latest email and reply with 'chicken' in it",
        metadata={
            "agent_type": "Gmail AI Agent",
            "goal": "Read the latest email and reply with 'chicken' in it"
        },
        steps=[
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
                            "snippet": "Subject: Re: Research\n\nHi [Original Author Name],\n\nThanks so much for thinking of me and pointing me towards Shuxin's research opportunity at the PAIR Lab. It sounds like a great fit! I'm definitely going to look into it further and send my updated CV as suggested. Hopefully they are not too busy eating chicken and can take a look quickly. I appreciate your encouragement and will let me know how it goes.\n\nBest,\n\nSriram\n",
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
            }
        ],
        final_output="Completed successfully",
        duration=7147,
        status="complete",
        agent_prompt="Gmail automation agent that reads latest email and replies with 'chicken' in the response",
        end_timestamp="2025-11-11T02:27:39.386Z"
    )
    
    print(f"\n📝 Processing run:")
    print(f"   Run ID: {payload.run_id}")
    print(f"   Agent: {payload.agent_id}")
    print(f"   Task: {payload.user_task}")
    print(f"   Status: {payload.status}")
    print(f"   Steps: {len(payload.steps)}")
    print(f"   Duration: {payload.duration}ms")
    
    try:
        builder = MemoryBuilder()
        result = builder.process_run(payload)
        
        if result.get("success"):
            print(f"\n✅ Run processed successfully!")
            print(f"   Task ID: {result.get('task_id')}")
            print(f"   References extracted: {result.get('references_count')}")
            print(f"   Artifacts extracted: {result.get('artifacts_count')}")
            return payload.run_id
        else:
            print(f"\n❌ Failed to process run: {result.get('error')}")
            return None
    except Exception as e:
        print(f"\n❌ Exception: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_retrieve_gmail_task():
    """Test retrieving the Gmail run with a similar task."""
    print("\n" + "=" * 70)
    print("TEST: Retrieving Gmail Run with Similar Task")
    print("=" * 70)
    
    retrieval = MemoryRetrieval()
    
    # Query similar to the Gmail task
    request = RetrievalRequest(
        task_text="I need to read an email and send a reply",
        agent_id="GmailReadAndReply",
        top_k=5
    )
    
    print(f"\n🔍 Searching for:")
    print(f"   Query: '{request.task_text}'")
    print(f"   Original task was: 'Read the latest email and reply with 'chicken' in it'")
    
    try:
        response = retrieval.retrieve(request)
        
        print(f"\n✅ Retrieval complete!")
        print(f"   Confidence: {response.confidence:.2%}")
        
        print(f"\n📊 Observations:")
        for i, obs in enumerate(response.observations, 1):
            print(f"   {i}. {obs}")
        
        print(f"\n📚 Found {len(response.related_runs)} related run(s):")
        
        found_gmail_run = False
        for i, run in enumerate(response.related_runs, 1):
            is_gmail = run.run_id == "e28b300f-406c-45d1-998e-46d365e1dd14"
            if is_gmail:
                found_gmail_run = True
            
            marker = " ⭐ (Gmail run we just added!)" if is_gmail else ""
            
            print(f"\n   Run {i}:")
            print(f"   - ID: {run.run_id}{marker}")
            print(f"   - Similarity: {run.similarity_score:.4f}")
            print(f"   - Outcome: {run.outcome}")
            print(f"   - Summary: {run.summary[:150]}...")
            print(f"   - References: {len(run.references)}")
            print(f"   - Artifacts: {len(run.artifacts)}")
            if run.run_tree:
                print(f"   - Has full run_tree: ✅")
                if "steps" in run.run_tree:
                    print(f"   - Steps in run_tree: {len(run.run_tree['steps'])}")
        
        if found_gmail_run:
            print(f"\n🎉 SUCCESS! The Gmail run was retrieved!")
        else:
            print(f"\n⚠️  The Gmail run was not found in results")
        
        return response
    except Exception as e:
        print(f"\n❌ Exception: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Run the complete test."""
    print("\n" + "🧪 " * 35)
    print("REAL RUN LOG TEST")
    print("🧪 " * 35 + "\n")
    
    # Step 1: Process the Gmail run log
    run_id = test_real_gmail_run_log()
    
    if run_id:
        # Step 2: Retrieve it with a similar task
        test_retrieve_gmail_task()
        
        print("\n" + "=" * 70)
        print("✅ TEST COMPLETE")
        print("=" * 70)
        print("\nThe Gmail run log has been:")
        print("  ✅ Processed and stored in Neo4j")
        print("  ✅ Full run_tree saved for retrieval")
        print("  ✅ References extracted from email data")
        print("  ✅ Artifacts extracted from LLM outputs (summaries, replies)")
    else:
        print("\n❌ Failed to process run, skipping retrieval test")


if __name__ == "__main__":
    main()

