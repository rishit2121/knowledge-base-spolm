"""
Test: Add one run (with summary + reason_added) and retrieve it.
Verifies the knowledge base stores and returns summary and reason_added.
"""
import random
import requests
import json
import uuid
from datetime import datetime

API_URL = "https://knowledge-base-spolm.vercel.app"
# API_URL = "http://localhost:8000"  # Uncomment for local testing

USER_ID = "rishit.agrawal121@gmail.com"
AGENT_ID = "IKuz0GgesfFtbA6mrD7J"


# Different task templates so each test run gets a new, distinct task (avoids NOT/redundant)
TASK_TEMPLATES = [
    {
        "user_task": "Design a TypeScript microservice that processes image uploads, generates thumbnails using Sharp, stores originals in S3, and exposes REST endpoints for upload and retrieval.",
        "steps": [
            {"step_id": "step1", "step_name": "setup_s3", "step_type": "tool_call", "step_input": {"action": "Configure AWS S3 client"}, "step_output": {"data": "S3 configured"}},
            {"step_id": "step2", "step_name": "upload_handler", "step_type": "tool_call", "step_input": {"action": "Create POST /upload endpoint"}, "step_output": {"data": "Upload endpoint ready"}},
            {"step_id": "step3", "step_name": "thumbnail", "step_type": "tool_call", "step_input": {"action": "Use Sharp to resize images"}, "step_output": {"data": "Thumbnails generated"}},
        ],
        "final_output": "Image processing microservice deployed with upload and thumbnail endpoints",
        "metadata": {"language": "TypeScript", "libraries": "Sharp, AWS SDK, Express"},
    },
    {
        "user_task": "Implement a Kotlin Android app that uses Room database to cache API responses, implements offline-first architecture with WorkManager for background sync, and displays data in RecyclerView.",
        "steps": [
            {"step_id": "step1", "step_name": "room_setup", "step_type": "tool_call", "step_input": {"action": "Define Room entities and DAO"}, "step_output": {"data": "Database schema created"}},
            {"step_id": "step2", "step_name": "repository", "step_type": "tool_call", "step_input": {"action": "Create Repository with API and DB sources"}, "step_output": {"data": "Repository implemented"}},
            {"step_id": "step3", "step_name": "workmanager", "step_type": "tool_call", "step_input": {"action": "Schedule periodic sync with WorkManager"}, "step_output": {"data": "Background sync configured"}},
        ],
        "final_output": "Android app with offline-first caching and background sync",
        "metadata": {"language": "Kotlin", "framework": "Android, Room, WorkManager"},
    },
    {
        "user_task": "Create a Swift iOS app using SwiftUI that integrates with Core ML to classify images from the camera, stores results in Core Data, and presents a history view with filters.",
        "steps": [
            {"step_id": "step1", "step_name": "camera", "step_type": "tool_call", "step_input": {"action": "AVFoundation camera capture"}, "step_output": {"data": "Camera ready"}},
            {"step_id": "step2", "step_name": "coreml", "step_type": "tool_call", "step_input": {"action": "Load MLModel and classify image"}, "step_output": {"data": "Classification complete"}},
            {"step_id": "step3", "step_name": "coredata", "step_type": "tool_call", "step_input": {"action": "Save results to Core Data"}, "step_output": {"data": "History saved"}},
        ],
        "final_output": "iOS app with real-time image classification and history",
        "metadata": {"language": "Swift", "framework": "SwiftUI, Core ML, Core Data"},
    },
    {
        "user_task": "Add a Rust CLI that reads a config TOML file, validates it, and prints a summary of loaded settings.",
        "steps": [
            {"step_id": "step1", "step_name": "parse_toml", "step_type": "tool_call", "step_input": {"action": "Parse TOML"}, "step_output": {"data": "Config struct"}},
            {"step_id": "step2", "step_name": "validate", "step_type": "tool_call", "step_input": {"action": "Validate fields"}, "step_output": {"data": "Valid"}},
        ],
        "final_output": "Config loaded and validated; summary printed",
        "metadata": {"language": "Rust", "crate": "toml"},
    },
    {
        "user_task": "Create a Node.js script that watches a directory for new files and runs a linter on each new or changed file.",
        "steps": [
            {"step_id": "step1", "step_name": "watch_setup", "step_type": "tool_call", "step_input": {"action": "chokidar watch dir"}, "step_output": {"data": "Watching"}},
            {"step_id": "step2", "step_name": "lint", "step_type": "tool_call", "step_input": {"action": "Run ESLint on changed file"}, "step_output": {"data": "Lint done"}},
        ],
        "final_output": "File watcher running; lint on change",
        "metadata": {"language": "Node.js", "tools": "chokidar, eslint"},
    },
    {
        "user_task": "Develop a C# .NET API that connects to PostgreSQL, implements JWT authentication, uses Entity Framework Core for migrations, and exposes GraphQL endpoints with Hot Chocolate.",
        "steps": [
            {"step_id": "step1", "step_name": "ef_setup", "step_type": "tool_call", "step_input": {"action": "Configure EF Core with PostgreSQL"}, "step_output": {"data": "Database context ready"}},
            {"step_id": "step2", "step_name": "jwt_auth", "step_type": "tool_call", "step_input": {"action": "Implement JWT token generation"}, "step_output": {"data": "Auth configured"}},
            {"step_id": "step3", "step_name": "graphql", "step_type": "tool_call", "step_input": {"action": "Set up Hot Chocolate GraphQL schema"}, "step_output": {"data": "GraphQL endpoint active"}},
        ],
        "final_output": ".NET API with PostgreSQL, JWT auth, and GraphQL",
        "metadata": {"language": "C#", "framework": ".NET, EF Core, Hot Chocolate"},
    },
]


def add_one_run():
    """POST one run to /runs (triggers summarization and decision; stores summary + reason_added). Uses a new task every time."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_id = f"test_summary_{timestamp}"
    unique_id = uuid.uuid4().hex[:12]  # e.g. a1b2c3d4e5f6
    t = random.choice(TASK_TEMPLATES)
    # Unique task text so embedding is never similar to past runs (avoids NOT/redundant)
    unique_task = f"{t['user_task']} [Unique scenario: {unique_id} | run: {timestamp}]"
    # Steps and output include unique_id so run content differs every time
    steps = []
    for s in t["steps"]:
        data = s.get("step_output", {}).get("data", "") + f" [{unique_id}]"
        steps.append({**s, "step_output": {"data": data}})
    payload = {
        "run_id": run_id,
        "agent_id": AGENT_ID,
        "user_id": USER_ID,
        "user_task": unique_task,
        "status": "complete",
        "steps": steps,
        "final_output": f"{t['final_output']} (id: {unique_id})",
        "metadata": {**t["metadata"], "unique_id": unique_id},
    }

    print("Adding run...")
    r = requests.post(f"{API_URL}/runs", json=payload, timeout=30)
    if r.status_code != 200:
        print(f"Add failed: {r.status_code} {r.text}")
        return None
    data = r.json()
    decision = data.get("data", {}).get("decision") or data.get("decision")
    decision_reason = data.get("data", {}).get("reason") or data.get("reason", "")
    data_payload = data.get("data", {})
    stored_summary = data_payload.get("summary")
    stored_reason_added = data_payload.get("reason_added")
    print(f"Decision: {decision}")
    print(f"Decision reason (internal): {decision_reason[:100]}...")
    if decision == "ADD":
        has_summary = bool((stored_summary or "").strip())
        has_reason = bool((stored_reason_added or "").strip())
        if not has_summary or not has_reason:
            print("  ⚠ POST response missing summary/reason_added. API may be old — deploy latest knowledge_base.")
        else:
            print("  ✓ Stored summary and reason_added returned in POST response.")
    return run_id


def retrieve_runs():
    """GET retrieve_all for user_id and agent_id; return list of runs with summary and reason_added."""
    url = f"{API_URL}/retrieve_all"
    params = {"user_id": USER_ID, "agent_id": AGENT_ID, "limit": 10}
    r = requests.get(url, params=params, timeout=30)
    if r.status_code != 200:
        print(f"Retrieve failed: {r.status_code} {r.text}")
        return []
    data = r.json()
    return data.get("runs", [])


def main():
    print("=" * 70)
    print("Test: Add one run and retrieve summary + reason_added")
    print("=" * 70)

    run_id = add_one_run()
    if not run_id:
        return

    print("\nRetrieving runs...")
    runs = retrieve_runs()
    if not runs:
        print("No runs returned.")
        return

    match = next((r for r in runs if r.get("run_id") == run_id), None)
    if not match:
        print(f"Run {run_id} not found in retrieve_all. Latest runs:")
        for r in runs[:3]:
            print(f"  - {r.get('run_id')} summary={str(r.get('summary', ''))[:80]}...")
        return

    print("\n" + "=" * 70)
    print("Retrieved run (summary + reason_added)")
    print("=" * 70)
    print("run_id:", match.get("run_id"))
    print("summary:", (match.get("summary") or "(none)")[:120] + ("..." if len(match.get("summary") or "") > 120 else ""))
    reason_added_val = match.get("reason_added")
    print("reason_added:", reason_added_val if reason_added_val else "(none)")
    print("outcome:", match.get("outcome"))

    # Diagnostics: one clear block
    print("\n--- Diagnostics ---")
    if "reason_added" not in match:
        print("⚠ 'reason_added' key missing from retrieve_all response. Deploy latest API (RunDetail must include reason_added).")
    elif not (reason_added_val or "").strip():
        print("⚠ reason_added is empty. Backend must store it when adding runs (LLM why_added or fallback). Deploy latest knowledge_base.")
    else:
        print("✓ reason_added present and non-empty.")
    print("------------------")
    ok = "reason_added" in match and bool((reason_added_val or "").strip())
    print("PASS: summary and reason_added stored and retrieved." if ok else "FAIL: reason_added missing or empty.")
    print("=" * 70)


if __name__ == "__main__":
    main()
