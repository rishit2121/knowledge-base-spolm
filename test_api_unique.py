"""
One-off test: Add a single run with a completely unique task (not similar to any template),
then retrieve it and verify summary + reason_added. Uses Vercel API.
"""
import sys
import requests
from datetime import datetime

API_URL = "https://knowledge-base-spolm.vercel.app"
USER_ID = "rishit.agrawal121@gmail.com"
AGENT_ID = "IKuz0GgesfFtbA6mrD7J"

# Two very different tasks so we can run test twice (second run uses task B)
USE_TASK_B = "--b" in sys.argv

if USE_TASK_B:
    UNIQUE_TASK = (
        "Build a Datalog engine in Racket that reads facts from CSV, compiles rules to a fixpoint evaluator, "
        "supports stratified negation and aggregation, and outputs query results as JSON. Include a REPL for ad-hoc queries."
    )
    UNIQUE_STEPS = [
        {"step_id": "s1", "step_name": "load_csv", "step_type": "tool_call", "step_input": {"action": "Load CSV facts"}, "step_output": {"data": "Facts loaded"}},
        {"step_id": "s2", "step_name": "compile", "step_type": "tool_call", "step_input": {"action": "Compile rules to fixpoint"}, "step_output": {"data": "Engine ready"}},
        {"step_id": "s3", "step_name": "eval", "step_type": "tool_call", "step_input": {"action": "Evaluate stratified program"}, "step_output": {"data": "Results computed"}},
        {"step_id": "s4", "step_name": "json_out", "step_type": "tool_call", "step_input": {"action": "Emit JSON"}, "step_output": {"data": "output.json"}},
    ]
    UNIQUE_OUTPUT = "Racket Datalog engine with REPL and JSON output."
    UNIQUE_METADATA = {"language": "Racket", "paradigm": "Datalog", "features": "stratified negation"}
else:
    UNIQUE_TASK = (
        "Build a Prolog expert system for medical differential diagnosis: use backward chaining "
        "to infer diseases from symptoms, load a knowledge base of symptom-disease rules from YAML, "
        "compute confidence scores with uncertainty propagation, and output a ranked differential "
        "diagnosis report as Markdown. Include a CLI with subcommands for query and reload."
    )
    UNIQUE_STEPS = [
        {"step_id": "s1", "step_name": "load_kb", "step_type": "tool_call", "step_input": {"action": "Parse YAML knowledge base"}, "step_output": {"data": "Rules loaded"}},
        {"step_id": "s2", "step_name": "backward_chain", "step_type": "tool_call", "step_input": {"action": "Run backward chaining inference"}, "step_output": {"data": "Candidates inferred"}},
        {"step_id": "s3", "step_name": "confidence", "step_type": "tool_call", "step_input": {"action": "Compute confidence scores"}, "step_output": {"data": "Ranked differential"}},
        {"step_id": "s4", "step_name": "report", "step_type": "tool_call", "step_input": {"action": "Emit Markdown report"}, "step_output": {"data": "report.md written"}},
    ]
    UNIQUE_OUTPUT = "Prolog medical expert system with backward chaining and differential diagnosis report."
    UNIQUE_METADATA = {"language": "Prolog", "domain": "medical", "paradigm": "expert system"}


def main():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_id = f"test_unique_{timestamp}"

    payload = {
        "run_id": run_id,
        "agent_id": AGENT_ID,
        "user_id": USER_ID,
        "user_task": UNIQUE_TASK,
        "status": "complete",
        "steps": UNIQUE_STEPS,
        "final_output": UNIQUE_OUTPUT,
        "metadata": UNIQUE_METADATA,
    }

    print("=" * 70)
    print("Test: Add unique run (Prolog medical expert system) and retrieve")
    print("=" * 70)
    print("Adding run...")
    r = requests.post(f"{API_URL}/runs", json=payload, timeout=60)
    if r.status_code != 200:
        print(f"Add failed: {r.status_code} {r.text}")
        return
    data = r.json()
    decision = data.get("data", {}).get("decision") or data.get("decision")
    print(f"Decision: {decision}")
    if decision != "ADD":
        print(f"Reason: {data.get('data', {}).get('reason', '')[:150]}...")
        print("Run was NOT added (similar to existing). Try again or use a different unique task.")
        return

    stored = data.get("data", {})
    print("POST response keys:", list(stored.keys()))
    s = stored.get("summary") or ""
    ra = stored.get("reason_added") or ""
    print(f"summary length: {len(s)}, reason_added length: {len(ra)}")
    if s:
        print(f"summary (first 120): {s[:120]}...")
    if ra:
        print(f"reason_added:\n{ra[:400]}{'...' if len(ra) > 400 else ''}")
    else:
        print("reason_added: (empty in POST response)")

    print("\nRetrieving runs...")
    resp = requests.get(
        f"{API_URL}/retrieve_all",
        params={"user_id": USER_ID, "agent_id": AGENT_ID, "limit": 10},
        timeout=30,
    )
    if resp.status_code != 200:
        print(f"Retrieve failed: {resp.status_code} {resp.text}")
        return
    runs = resp.json().get("runs", [])
    match = next((x for x in runs if x.get("run_id") == run_id), None)
    if not match:
        print(f"Run {run_id} not found in retrieve_all.")
        return

    print("\n" + "=" * 70)
    print("Retrieved run")
    print("=" * 70)
    print("run_id:", match.get("run_id"))
    print("summary:", (match.get("summary") or "(none)")[:150] + "...")
    print("reason_added:", match.get("reason_added") or "(none)")
    print("outcome:", match.get("outcome"))
    has_reason = "reason_added" in match and (match.get("reason_added") or "").strip()
    print("\n" + ("PASS: summary and reason_added stored and retrieved." if has_reason else "FAIL: reason_added missing or empty."))
    print("=" * 70)


if __name__ == "__main__":
    main()
