# Quick Vercel Deployment Guide

## Prerequisites

1. **Install Vercel CLI**:
   ```bash
   npm i -g vercel
   ```

2. **Login**:
   ```bash
   vercel login
   ```

## Quick Deploy Steps

### 1. Set Environment Variables

You can set them via CLI or dashboard. **Via CLI** (recommended):

```bash
# Neo4j
vercel env add NEO4J_URI production
vercel env add NEO4J_USER production
vercel env add NEO4J_PASSWORD production

# Provider (choose one)
vercel env add PROVIDER production
# Then set either:
vercel env add OPENAI_API_KEY production
# OR
vercel env add GEMINI_API_KEY production
```

**Via Dashboard**:
1. Go to https://vercel.com/dashboard
2. Create/select your project
3. Settings → Environment Variables
4. Add each variable

### 2. Deploy

```bash
# First time (follow prompts)
vercel

# Production
vercel --prod
```

### 3. Test

Your API will be at: `https://your-project.vercel.app/`

```bash
# Health check
curl https://your-project.vercel.app/

# Test endpoint
curl https://your-project.vercel.app/stats
```

## Required Environment Variables

Set these in Vercel (all environments):

- `NEO4J_URI` - Your Neo4j Aura URI
- `NEO4J_USER` - Usually `neo4j`
- `NEO4J_PASSWORD` - Your Neo4j password
- `PROVIDER` - `openai` or `gemini`
- `OPENAI_API_KEY` - If using OpenAI
- `GEMINI_API_KEY` - If using Gemini

## Important Notes

⚠️ **Cold Starts**: First request after inactivity may be slow (5-10 seconds)

⚠️ **Timeouts**: 
- Free tier: 10 seconds max
- Pro: 60 seconds
- If your runs take longer, process them asynchronously

⚠️ **File Size**: Request body limit is 4.5MB

## Troubleshooting

**"Module not found"**: All dependencies in `requirements.txt` are installed automatically

**"Connection timeout"**: Check Neo4j Aura allows external connections

**"Environment variable missing"**: Set in Vercel dashboard and redeploy

## Update Your Test Script

After deployment, update `test_add_and_retrieve.py`:

```python
# Change this line:
api_url = "https://your-project.vercel.app"
```

Then test:
```bash
python test_add_and_retrieve.py https://your-project.vercel.app
```

