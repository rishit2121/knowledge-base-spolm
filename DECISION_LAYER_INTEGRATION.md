# Decision Layer Integration Status

## ✅ Already Integrated!

The decision layer is **already fully integrated** into the `/runs` endpoint. Every time you call:

```bash
POST /runs
```

The system automatically:
1. Processes the run
2. **Runs the decision layer** (ADD/NOT/REPLACE/MERGE)
3. Returns the decision in the response

## API Response Format

When you call `/runs`, you get:

```json
{
  "status": "success",
  "message": "Run processed and stored successfully",
  "data": {
    "success": true,
    "decision": "ADD|NOT|REPLACE|MERGE",
    "run_id": "run_123",
    "task_id": "task_456",
    "references_count": 2,
    "artifacts_count": 1,
    "target_run_id": "run_789",  // Only for REPLACE/MERGE
    "reason": "No similar runs found in memory"
  }
}
```

## Recent Fixes

### 1. JSON Parsing Improvements
- ✅ Added `response_mime_type: "application/json"` to Gemini config (forces JSON)
- ✅ Improved prompt to be more explicit about JSON format
- ✅ Better JSON extraction (handles markdown code blocks)
- ✅ Handles `null` for `target_run_id` properly

### 2. Rate Limit Handling
- ✅ Better error messages for Gemini rate limits
- ✅ Clear indication when quota is exceeded
- ✅ Suggests waiting before retry

### 3. Dimension Mismatch Fix
- ✅ Skips old embeddings with wrong dimensions
- ✅ Only compares embeddings with same dimension

## Testing

You don't need to run `test_decision_layer.py` every time. Just use the API:

```bash
curl -X POST http://localhost:8000/runs \
  -H "Content-Type: application/json" \
  -d '{
    "run_id": "test_123",
    "agent_id": "my_agent",
    "user_task": "Generate a schema",
    "status": "complete",
    "steps": []
  }'
```

The decision layer runs automatically!

## Rate Limits

**Gemini Free Tier**: 5 requests per minute per model

If you hit rate limits:
1. Wait ~35 seconds between requests
2. Or upgrade to paid tier
3. Or use OpenAI instead (higher limits)

## Next Steps

1. **Deploy to Vercel** - The decision layer is already integrated, just deploy!
2. **Monitor decisions** - Check the `MemoryDecision` nodes in Neo4j
3. **Tune thresholds** - Adjust similarity thresholds in `services/decision.py`

