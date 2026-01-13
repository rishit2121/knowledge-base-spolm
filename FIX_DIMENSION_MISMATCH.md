# Fix Embedding Dimension Mismatch

## Problem
Your Neo4j vector indexes were created with dimension 3072, but Gemini embeddings are 768 dimensions. This causes the error:
```
shapes (768,) and (3072,) not aligned: 768 (dim 0) != 3072 (dim 0)
```

## Solution

You have two options:

### Option 1: Fix via Script (Recommended)

Run the fix script locally (it will connect to your Neo4j Aura instance):

```bash
python fix_embedding_dimensions.py
```

This will:
1. Drop existing vector indexes
2. Recreate them with the correct dimension (768 for Gemini)

### Option 2: Fix via Neo4j Browser

1. Go to your Neo4j Aura dashboard
2. Click "Open" to open Neo4j Browser
3. Run these commands:

```cypher
// Drop existing indexes
DROP INDEX task_embedding_index IF EXISTS;
DROP INDEX run_embedding_index IF EXISTS;
DROP INDEX reference_embedding_index IF EXISTS;
DROP INDEX artifact_embedding_index IF EXISTS;
```

Then run `init_db.py` again (it will recreate indexes with correct dimensions):

```bash
python init_db.py
```

### Option 3: Clear All Embeddings (Nuclear Option)

If you have existing data with wrong dimensions, you may need to clear it:

```cypher
// In Neo4j Browser
MATCH (n)
WHERE n.embedding IS NOT NULL
SET n.embedding = null;
```

Then run `init_db.py` to recreate indexes, and reprocess your runs.

## After Fixing

1. Make sure your `.env` has:
   ```
   PROVIDER=gemini
   GEMINI_EMBEDDING_MODEL=text-embedding-004
   ```

2. Verify the fix worked:
   ```bash
   python test_add_and_retrieve.py
   ```

## For Vercel Deployment

After fixing locally, make sure your Vercel environment variables are set correctly:
- `PROVIDER=gemini`
- `GEMINI_EMBEDDING_MODEL=text-embedding-004`

The fix script connects to the same Neo4j Aura instance that Vercel uses, so running it locally will fix the production database.


