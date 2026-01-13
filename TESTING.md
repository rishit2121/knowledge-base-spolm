# Testing Your Knowledge Base API

## Quick Test

Run the test script:

```bash
python test_add_and_retrieve.py
```

This will:
1. ✅ Check if the API is running
2. 📝 Add a test run to the knowledge base
3. 🔍 Retrieve it using a similar query
4. ✅ Verify the run was found

## What to Expect

### Success Output:
```
✅ API server is running
✅ Run added successfully via API!
✅ Retrieval complete via API!
🎉 SUCCESS! The run we just added was retrieved via API!
```

### If You Get Dimension Errors:
Run the fix script first:
```bash
python fix_embedding_dimensions.py
```

## Testing Locally

If you want to test against a local API instead of Vercel:

1. Start the API:
   ```bash
   python api.py
   ```

2. Run test with localhost:
   ```bash
   python test_add_and_retrieve.py http://localhost:8000
   ```

## Testing Other Endpoints

### Health Check
```bash
curl https://knowledge-base-spolm.vercel.app/
```

### Stats
```bash
curl https://knowledge-base-spolm.vercel.app/stats
```

### Add a Run (POST)
```bash
curl -X POST https://knowledge-base-spolm.vercel.app/runs \
  -H "Content-Type: application/json" \
  -d @test_payload.json
```

### Retrieve (POST)
```bash
curl -X POST https://knowledge-base-spolm.vercel.app/retrieve \
  -H "Content-Type: application/json" \
  -d '{
    "task_text": "Read email and reply",
    "agent_id": "GmailReadAndReply",
    "top_k": 5
  }'
```

## Troubleshooting

### "500 Server Error: shapes not aligned"
- Run: `python fix_embedding_dimensions.py`
- Make sure `PROVIDER=gemini` in your `.env`

### "Could not connect to API server"
- Check if Vercel deployment is successful
- Wait a few seconds (cold start on first request)
- Verify the URL is correct

### "GEMINI_API_KEY must be set"
- Check your `.env` file has `GEMINI_API_KEY`
- Check Vercel environment variables


