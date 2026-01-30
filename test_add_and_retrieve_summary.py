"""
Test: Add one run (with summary + reason_added) and retrieve it.
Verifies the knowledge base stores and returns summary and reason_added.

Vercel Deployment Protection (401):
  Use a bypass token (safest): Vercel → Project → Settings → Deployment Protection
  → "Protection Bypass for Automation" → create/copy secret. Put it in .env (see below).
"""
import os
import random
import requests
import json
import uuid
from datetime import datetime

# Load .env from this directory so VERCEL_BYPASS_TOKEN and KB_API_URL can be set there (never commit .env)
try:
    from dotenv import load_dotenv
    _env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    load_dotenv(_env_path)
except ImportError:
    pass

API_URL = (os.environ.get("KB_API_URL") or "https://knowledge-base-spolm.vercel.app").rstrip("/")
# Preview: KB_API_URL=https://knowledge-base-spolm-okcuwvgyl.vercel.app in .env
# Local: KB_API_URL=http://localhost:8000

VERCEL_BYPASS_TOKEN = os.environ.get("VERCEL_BYPASS_TOKEN")  # In .env or export; from Vercel → Deployment Protection → Bypass

USER_ID = "rishit.agrawal121@gmail.com"
AGENT_ID = "IKuz0GgesfFtbA6mrD7J"


def _url(path):
    """Build full URL with optional Vercel bypass token."""
    base = f"{API_URL}{path}"
    if VERCEL_BYPASS_TOKEN:
        sep = "&" if "?" in base else "?"
        base = f"{base}{sep}x-vercel-set-bypass-cookie=true&x-vercel-protection-bypass={VERCEL_BYPASS_TOKEN}"
    return base


# Different task templates so each test run gets a new, distinct task (avoids NOT/redundant)
TASK_TEMPLATES = [
    {
        "user_task": "Build a Zig compiler toolchain that parses source files, performs semantic analysis, generates LLVM IR, and outputs optimized machine code for ARM64 architecture.",
        "steps": [
            {"step_id": "step1", "step_name": "lexer", "step_type": "tool_call", "step_input": {"action": "Tokenize source code"}, "step_output": {"data": "Tokens generated"}},
            {"step_id": "step2", "step_name": "parser", "step_type": "tool_call", "step_input": {"action": "Build AST from tokens"}, "step_output": {"data": "AST constructed"}},
            {"step_id": "step3", "step_name": "codegen", "step_type": "tool_call", "step_input": {"action": "Emit LLVM IR and optimize"}, "step_output": {"data": "Binary compiled"}},
        ],
        "final_output": "Zig compiler toolchain producing ARM64 binaries",
        "metadata": {"language": "Zig", "target": "ARM64, LLVM"},
    },
    {
        "user_task": "Create an Elixir Phoenix LiveView application that streams real-time sensor data from IoT devices via WebSockets, aggregates metrics using GenServer, and visualizes trends with SVG charts.",
        "steps": [
            {"step_id": "step1", "step_name": "websocket", "step_type": "tool_call", "step_input": {"action": "Set up Phoenix channels"}, "step_output": {"data": "WebSocket connected"}},
            {"step_id": "step2", "step_name": "genserver", "step_type": "tool_call", "step_input": {"action": "Aggregate sensor readings"}, "step_output": {"data": "Metrics computed"}},
            {"step_id": "step3", "step_name": "visualization", "step_type": "tool_call", "step_input": {"action": "Render SVG charts in LiveView"}, "step_output": {"data": "Dashboard updated"}},
        ],
        "final_output": "Real-time IoT dashboard with live sensor streaming",
        "metadata": {"language": "Elixir", "framework": "Phoenix LiveView, GenServer"},
    },
    {
        "user_task": "Develop a Julia scientific computing pipeline that loads astronomical data from FITS files, performs spectral analysis using FFTW, fits models with Optim.jl, and generates publication-quality plots with Plots.jl.",
        "steps": [
            {"step_id": "step1", "step_name": "load_data", "step_type": "tool_call", "step_input": {"action": "Read FITS files"}, "step_output": {"data": "Data loaded"}},
            {"step_id": "step2", "step_name": "fft", "step_type": "tool_call", "step_input": {"action": "Compute FFT spectrum"}, "step_output": {"data": "Frequency domain"}},
            {"step_id": "step3", "step_name": "fit", "step_type": "tool_call", "step_input": {"action": "Optimize model parameters"}, "step_output": {"data": "Model fitted"}},
        ],
        "final_output": "Astronomical data analysis pipeline with spectral fitting",
        "metadata": {"language": "Julia", "packages": "FITSIO, FFTW, Optim, Plots"},
    },
    {
        "user_task": "Implement a Haskell web service using Servant that provides a REST API for managing a distributed ledger, uses STM for concurrent transactions, and persists state with Persistent and PostgreSQL.",
        "steps": [
            {"step_id": "step1", "step_name": "servant_api", "step_type": "tool_call", "step_input": {"action": "Define Servant API types"}, "step_output": {"data": "API types defined"}},
            {"step_id": "step2", "step_name": "stm", "step_type": "tool_call", "step_input": {"action": "Implement STM transaction logic"}, "step_output": {"data": "Concurrent transactions"}},
            {"step_id": "step3", "step_name": "persistent", "step_type": "tool_call", "step_input": {"action": "Set up Persistent migrations"}, "step_output": {"data": "Database schema"}},
        ],
        "final_output": "Haskell distributed ledger service with STM concurrency",
        "metadata": {"language": "Haskell", "libraries": "Servant, STM, Persistent"},
    },
    {
        "user_task": "Build a Lua script for Neovim that creates a custom LSP client, integrates with nvim-treesitter for syntax highlighting, and implements a fuzzy finder using telescope.nvim.",
        "steps": [
            {"step_id": "step1", "step_name": "lsp", "step_type": "tool_call", "step_input": {"action": "Configure LSP client"}, "step_output": {"data": "LSP attached"}},
            {"step_id": "step2", "step_name": "treesitter", "step_type": "tool_call", "step_input": {"action": "Set up treesitter parsers"}, "step_output": {"data": "Syntax highlighting"}},
            {"step_id": "step3", "step_name": "telescope", "step_type": "tool_call", "step_input": {"action": "Create custom picker"}, "step_output": {"data": "Fuzzy finder ready"}},
        ],
        "final_output": "Neovim plugin with LSP, treesitter, and telescope integration",
        "metadata": {"language": "Lua", "platform": "Neovim, LSP, treesitter"},
    },
    {
        "user_task": "Create a Crystal web framework application that uses Kemal for routing, connects to Redis for caching, implements WebSocket chat rooms, and serves static assets with HTTP/2 push.",
        "steps": [
            {"step_id": "step1", "step_name": "kemal", "step_type": "tool_call", "step_input": {"action": "Set up Kemal routes"}, "step_output": {"data": "Routes configured"}},
            {"step_id": "step2", "step_name": "redis", "step_type": "tool_call", "step_input": {"action": "Connect to Redis cache"}, "step_output": {"data": "Cache connected"}},
            {"step_id": "step3", "step_name": "websocket", "step_type": "tool_call", "step_input": {"action": "Implement chat rooms"}, "step_output": {"data": "Chat active"}},
        ],
        "final_output": "Crystal web app with Redis caching and WebSocket chat",
        "metadata": {"language": "Crystal", "framework": "Kemal, Redis, HTTP/2"},
    },
    {
        "user_task": "Develop a Nim systems programming application that implements a custom memory allocator using arena allocation, integrates with libuv for async I/O, and provides a zero-copy serialization format using flatbuffers.",
        "steps": [
            {"step_id": "step1", "step_name": "allocator", "step_type": "tool_call", "step_input": {"action": "Implement arena allocator"}, "step_output": {"data": "Memory allocator ready"}},
            {"step_id": "step2", "step_name": "libuv", "step_type": "tool_call", "step_input": {"action": "Set up async event loop"}, "step_output": {"data": "Async I/O configured"}},
            {"step_id": "step3", "step_name": "flatbuffers", "step_type": "tool_call", "step_input": {"action": "Generate serialization code"}, "step_output": {"data": "Zero-copy serialization"}},
        ],
        "final_output": "Nim systems app with custom allocator and async I/O",
        "metadata": {"language": "Nim", "libraries": "libuv, flatbuffers"},
    },
    {
        "user_task": "Create a Clojure web application using Ring and Compojure that processes financial transaction data, uses core.async channels for concurrent processing, stores results in Datomic, and exposes a REST API with Swagger documentation.",
        "steps": [
            {"step_id": "step1", "step_name": "ring_setup", "step_type": "tool_call", "step_input": {"action": "Set up Ring handlers"}, "step_output": {"data": "Routes configured"}},
            {"step_id": "step2", "step_name": "core_async", "step_type": "tool_call", "step_input": {"action": "Create async processing pipeline"}, "step_output": {"data": "Channels active"}},
            {"step_id": "step3", "step_name": "datomic", "step_type": "tool_call", "step_input": {"action": "Store transactions in Datomic"}, "step_output": {"data": "Data persisted"}},
            {"step_id": "step4", "step_name": "swagger", "step_type": "tool_call", "step_input": {"action": "Generate Swagger docs"}, "step_output": {"data": "API documented"}},
        ],
        "final_output": "Clojure financial API with async processing and Datomic storage",
        "metadata": {"language": "Clojure", "stack": "Ring, Compojure, core.async, Datomic"},
    },
    {
        "user_task": "Build an OCaml compiler frontend that parses ML source code, performs type inference using Hindley-Milner algorithm, generates intermediate representation, and outputs optimized bytecode for the OCaml virtual machine.",
        "steps": [
            {"step_id": "step1", "step_name": "parser", "step_type": "tool_call", "step_input": {"action": "Parse ML syntax to AST"}, "step_output": {"data": "AST generated"}},
            {"step_id": "step2", "step_name": "typecheck", "step_type": "tool_call", "step_input": {"action": "Run Hindley-Milner type inference"}, "step_output": {"data": "Types inferred"}},
            {"step_id": "step3", "step_name": "lambda", "step_type": "tool_call", "step_input": {"action": "Convert to lambda calculus IR"}, "step_output": {"data": "IR ready"}},
            {"step_id": "step4", "step_name": "bytecode", "step_type": "tool_call", "step_input": {"action": "Emit OCaml bytecode"}, "step_output": {"data": "Bytecode compiled"}},
        ],
        "final_output": "OCaml compiler frontend with type inference and bytecode generation",
        "metadata": {"language": "OCaml", "domain": "compiler", "algorithm": "Hindley-Milner"},
    },
    {
        "user_task": "Develop a Forth interpreter that implements a virtual machine with dictionary-based word lookup, supports immediate and compile-time words, provides a REPL with history, and can save/load dictionary state to binary files.",
        "steps": [
            {"step_id": "step1", "step_name": "vm", "step_type": "tool_call", "step_input": {"action": "Implement stack-based VM"}, "step_output": {"data": "VM running"}},
            {"step_id": "step2", "step_name": "dictionary", "step_type": "tool_call", "step_input": {"action": "Build word dictionary"}, "step_output": {"data": "Dictionary ready"}},
            {"step_id": "step3", "step_name": "repl", "step_type": "tool_call", "step_input": {"action": "Create REPL with history"}, "step_output": {"data": "REPL active"}},
            {"step_id": "step4", "step_name": "persist", "step_type": "tool_call", "step_input": {"action": "Save dictionary to binary"}, "step_output": {"data": "State saved"}},
        ],
        "final_output": "Forth interpreter with VM, dictionary, REPL, and persistence",
        "metadata": {"language": "Forth", "features": "stack-based VM, dictionary, REPL"},
    },
    {
        "user_task": "Build an Erlang OTP supervision tree for a distributed key-value store: gen_server for shard state, gen_event for audit logging, supervisor for restart strategy, and libcluster for node discovery across Kubernetes pods.",
        "steps": [
            {"step_id": "step1", "step_name": "gen_server", "step_type": "tool_call", "step_input": {"action": "Implement shard gen_server"}, "step_output": {"data": "Shard server running"}},
            {"step_id": "step2", "step_name": "gen_event", "step_type": "tool_call", "step_input": {"action": "Add audit event handler"}, "step_output": {"data": "Audit logging active"}},
            {"step_id": "step3", "step_name": "supervisor", "step_type": "tool_call", "step_input": {"action": "One-for-one supervisor tree"}, "step_output": {"data": "Supervision configured"}},
            {"step_id": "step4", "step_name": "libcluster", "step_type": "tool_call", "step_input": {"action": "Kubernetes DNS node discovery"}, "step_output": {"data": "Cluster formed"}},
        ],
        "final_output": "Erlang OTP distributed KV store with supervision and cluster",
        "metadata": {"language": "Erlang", "framework": "OTP", "gen_server": "true", "libcluster": "true"},
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
    r = requests.post(_url("/runs"), json=payload, timeout=30)
    if r.status_code != 200:
        print(f"Add failed: {r.status_code} {r.text[:500]}...")
        if r.status_code == 401:
            print("\n401 = Vercel Deployment Protection. Either:")
            print("  1. Vercel → Project → Settings → Deployment Protection → disable or set to 'Only Production'")
            print("  2. Or set VERCEL_BYPASS_TOKEN (get token from same page) and KB_API_URL to your deployment URL")
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
        print("\n[DEBUG] Full API response data payload:")
        print(f"  Keys in data: {list(data_payload.keys())}")
        print(f"  summary: {repr((stored_summary or '')[:200])}")
        print(f"  reason_added: {repr((stored_reason_added or '')[:400])}")
        has_summary = bool((stored_summary or "").strip())
        has_reason = bool((stored_reason_added or "").strip())
        if not has_summary or not has_reason:
            print("  ⚠ POST response missing summary/reason_added. API may be old — deploy latest knowledge_base.")
        else:
            print("  ✓ Stored summary and reason_added returned in POST response.")
    return run_id


def retrieve_runs():
    """GET retrieve_all for user_id and agent_id; return list of runs with summary and reason_added."""
    url = _url("/retrieve_all")
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
