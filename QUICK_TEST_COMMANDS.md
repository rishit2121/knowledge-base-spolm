# Quick Test Commands

## Option 1: Run the Complete Test Script (Recommended)

This adds a run and then retrieves it:

```bash
python test_add_and_retrieve.py
```

This will:
1. Add a run about "Building a REST API for user profile management"
2. Retrieve it using a similar query: "Create API endpoints to manage user profiles"
3. Show you the results including similarity scores

---

## Option 2: Manual Commands (Step by Step)

### Step 1: Add a Run

Create a file `add_run.py`:

```python
from datetime import datetime
from models.run import RunPayload
from memory_builder import MemoryBuilder

payload = RunPayload(
    run_id=f"test_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
    task_text="Build a REST API endpoint for user profile management with CRUD operations",
    agent_id="test_agent",
    run_tree={
        "steps": [
            {"type": "reference", "source": "schema", "content": "User profile schema"},
            {"type": "artifact", "type": "code", "content": "@app.get('/users/{user_id}')..."}
        ],
        "reasoning": "Need RESTful API endpoints",
        "tools_used": ["fastapi"]
    },
    outcome="success",
    created_at=datetime.utcnow()
)

builder = MemoryBuilder()
result = builder.process_run(payload)
print(f"Result: {result}")
```

Run it:
```bash
python add_run.py
```

### Step 2: Retrieve with Similar Task

Create a file `retrieve.py`:

```python
from models.retrieval import RetrievalRequest
from memory_retrieval import MemoryRetrieval

retrieval = MemoryRetrieval()
request = RetrievalRequest(
    task_text="Create API endpoints to manage user profiles",  # Similar but not exact
    top_k=5
)

response = retrieval.retrieve(request)
print(f"Confidence: {response.confidence}")
print(f"Found {len(response.related_runs)} runs")
for run in response.related_runs:
    print(f"  - {run.run_id}: similarity={run.similarity_score:.3f}, outcome={run.outcome}")
```

Run it:
```bash
python retrieve.py
```

---

## Option 3: Using the API

### Start the API server:
```bash
python api.py
```

### Add a run (in another terminal):
```bash
curl -X POST "http://localhost:8000/runs" \
  -H "Content-Type: application/json" \
  -d '{
    "run_id": "test_run_001",
    "task_text": "Build a REST API endpoint for user profile management with CRUD operations",
    "agent_id": "test_agent",
    "run_tree": {
      "steps": [
        {"type": "reference", "source": "schema", "content": "User profile schema"},
        {"type": "artifact", "type": "code", "content": "API code here"}
      ],
      "reasoning": "Need RESTful API endpoints"
    },
    "outcome": "success"
  }'
```

### Retrieve with similar task:
```bash
curl -X POST "http://localhost:8000/retrieve" \
  -H "Content-Type: application/json" \
  -d '{
    "task_text": "Create API endpoints to manage user profiles",
    "top_k": 5
  }'
```

---

## Expected Results

When you run the test, you should see:

1. **Adding the run:**
   - ✅ Run added successfully
   - Task ID, References count, Artifacts count

2. **Retrieving:**
   - ✅ Found the run you just added
   - Similarity score (should be > 0.85)
   - Full summary and run_tree
   - Observations about the run

The key test is that even though you query with "Create API endpoints to manage user profiles" (different wording), it should find the run you added with "Build a REST API endpoint for user profile management" because they're semantically similar!

