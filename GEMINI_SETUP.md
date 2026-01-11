# Using Gemini Instead of OpenAI

## Quick Setup

### 1. Install Gemini Package

```bash
pip install google-generativeai
```

Or install all requirements:
```bash
pip install -r requirements.txt
```

### 2. Get Gemini API Key

1. Go to https://aistudio.google.com/app/apikey
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the API key

### 3. Update Your .env File

Add these lines to your `.env`:

```env
# Switch to Gemini
PROVIDER=gemini

# Gemini API Key
GEMINI_API_KEY=your_gemini_api_key_here

# Optional: Customize models (defaults shown)
GEMINI_EMBEDDING_MODEL=gemini-embedding-1.0
GEMINI_CHAT_MODEL=gemini-2.5-flash
```

### 4. That's It!

The system will automatically use Gemini for:
- **Embeddings**: `gemini-embedding-1.0` (768 dimensions)
- **Chat/Summarization**: `gemini-2.5-flash`

## Switching Back to OpenAI

Just change in `.env`:
```env
PROVIDER=openai
OPENAI_API_KEY=your_openai_key
```

## Cost Comparison

### Gemini 2.0 Flash
- **Embeddings**: ~$0.0001 per 1K characters
- **Chat**: ~$0.075 per 1M input tokens, ~$0.30 per 1M output tokens
- **Much cheaper** than GPT-4!

### OpenAI
- **Embeddings**: ~$0.02 per 1M tokens
- **GPT-4**: ~$10 per 1M input tokens, ~$30 per 1M output tokens

## Notes

- Gemini embeddings are **768 dimensions** (vs OpenAI's 1536)
- The system automatically adjusts for this
- Both work identically from your perspective - just change `PROVIDER`!

## Troubleshooting

### "google-generativeai package is required"
```bash
pip install google-generativeai
```

### "GEMINI_API_KEY must be set"
Make sure you added `GEMINI_API_KEY=...` to your `.env` file

### Embedding dimension mismatch
The system handles this automatically, but if you see issues, make sure `EMBEDDING_DIMENSION` matches:
- Gemini: 768
- OpenAI: 1536

