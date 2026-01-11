# Available Gemini Models

Based on your API, here are the available models:

## Embedding Models

1. **`text-embedding-004`** (Default) ✅
   - Standard embedding model
   - 768 dimensions
   - Methods: `embedContent`

2. **`gemini-embedding-001`** (Recommended for batch operations)
   - Newer embedding model
   - 768 dimensions  
   - Methods: `embedContent`, `countTextTokens`, `countTokens`, `asyncBatchEmbedContent`
   - **Has batch support!**

3. **`embedding-001`**
   - Methods: `embedContent`

4. **`gemini-embedding-exp`** (Experimental)
   - Methods: `embedContent`, `countTextTokens`, `countTokens`

5. **`gemini-embedding-exp-03-07`** (Experimental)
   - Methods: `embedContent`, `countTextTokens`, `countTokens`

## Chat Models

1. **`gemini-2.5-flash`** (Default) ✅
   - Fast and efficient
   - Methods: `generateContent`, `countTokens`, `createCachedContent`, `batchGenerateContent`

2. **`gemini-2.5-pro`**
   - More powerful, slower
   - Methods: `generateContent`, `countTokens`, `createCachedContent`, `batchGenerateContent`

3. **`gemini-2.0-flash`**
   - Previous generation
   - Methods: `generateContent`, `countTokens`, `createCachedContent`, `batchGenerateContent`

## Recommended Configuration

For best performance with batch operations:

```env
GEMINI_EMBEDDING_MODEL=gemini-embedding-001
GEMINI_CHAT_MODEL=gemini-2.5-flash
```

For standard use (current default):

```env
GEMINI_EMBEDDING_MODEL=text-embedding-004
GEMINI_CHAT_MODEL=gemini-2.5-flash
```

## Note

All model names in your `.env` file should be **without** the `models/` prefix. The code automatically adds it.

Example:
- ✅ Correct: `GEMINI_EMBEDDING_MODEL=text-embedding-004`
- ❌ Wrong: `GEMINI_EMBEDDING_MODEL=models/text-embedding-004`

