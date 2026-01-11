# Deploying to Vercel

## Prerequisites

1. **Vercel account**: Sign up at https://vercel.com
2. **Vercel CLI**: Install with `npm i -g vercel`
3. **Environment variables**: Have your credentials ready

## Step-by-Step Deployment

### 1. Install Vercel CLI (if not already installed)

```bash
npm i -g vercel
```

### 2. Login to Vercel

```bash
vercel login
```

### 3. Set Up Environment Variables

You need to set these in Vercel dashboard or via CLI:

**Required:**
- `NEO4J_URI` - Your Neo4j Aura connection URI
- `NEO4J_USER` - Neo4j username (usually `neo4j`)
- `NEO4J_PASSWORD` - Neo4j password
- `PROVIDER` - Either `openai` or `gemini`
- `OPENAI_API_KEY` - If using OpenAI
- `GEMINI_API_KEY` - If using Gemini

**Optional:**
- `EMBEDDING_MODEL` - Override default embedding model
- `EMBEDDING_DIMENSION` - Embedding dimension (default: 1536 for OpenAI, 768 for Gemini)
- `SIMILARITY_THRESHOLD` - Similarity threshold (default: 0.85)
- `API_HOST` - Not needed for Vercel
- `API_PORT` - Not needed for Vercel

### 4. Set Environment Variables via CLI

```bash
# Neo4j
vercel env add NEO4J_URI
vercel env add NEO4J_USER
vercel env add NEO4J_PASSWORD

# Provider
vercel env add PROVIDER

# API Keys (choose one based on provider)
vercel env add OPENAI_API_KEY  # If using OpenAI
vercel env add GEMINI_API_KEY  # If using Gemini

# Optional
vercel env add EMBEDDING_DIMENSION
vercel env add SIMILARITY_THRESHOLD
```

Or set them in the Vercel dashboard:
1. Go to your project settings
2. Navigate to "Environment Variables"
3. Add each variable

### 5. Deploy

```bash
# First deployment (follow prompts)
vercel

# Production deployment
vercel --prod
```

### 6. Update vercel.json (if needed)

The `vercel.json` file is already configured, but you may need to adjust environment variable names if you set them differently in Vercel.

## Alternative: Deploy via GitHub

1. **Push to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```

2. **Import to Vercel**:
   - Go to https://vercel.com/new
   - Import your GitHub repository
   - Add environment variables in the Vercel dashboard
   - Deploy

## API Endpoints After Deployment

Once deployed, your API will be available at:
- `https://your-project.vercel.app/` - Health check
- `https://your-project.vercel.app/runs` - POST to add runs
- `https://your-project.vercel.app/retrieve` - POST to retrieve memory
- `https://your-project.vercel.app/stats` - GET statistics
- `https://your-project.vercel.app/docs` - API documentation

## Important Notes

1. **Cold Starts**: Vercel functions have cold starts. First request may be slow.

2. **Timeout**: Vercel has execution time limits:
   - Hobby: 10 seconds
   - Pro: 60 seconds
   - Enterprise: 300 seconds
   
   If your runs take longer, consider:
   - Processing runs asynchronously
   - Using background jobs
   - Splitting into smaller operations

3. **File Size Limits**: 
   - Request body: 4.5MB (Hobby), 4.5MB (Pro)
   - If your run logs are very large, you may need to optimize

4. **Neo4j Connection**: 
   - Make sure your Neo4j Aura instance allows connections from Vercel's IPs
   - Aura should work fine as it's cloud-based

5. **Environment Variables**:
   - Set them for all environments (Production, Preview, Development)
   - Or use `vercel env pull` to sync locally

## Testing After Deployment

```bash
# Test health check
curl https://your-project.vercel.app/

# Test adding a run
curl -X POST https://your-project.vercel.app/runs \
  -H "Content-Type: application/json" \
  -d @your_run_log.json

# Test retrieval
curl -X POST https://your-project.vercel.app/retrieve \
  -H "Content-Type: application/json" \
  -d '{"task_text": "your task", "top_k": 5}'
```

## Troubleshooting

### "Module not found" errors
- Make sure all dependencies are in `requirements.txt`
- Vercel installs from `requirements.txt` automatically

### "Connection timeout" to Neo4j
- Check Neo4j Aura firewall settings
- Verify `NEO4J_URI` is correct (should be `neo4j+s://...`)

### "Environment variable not set"
- Make sure variables are set in Vercel dashboard
- Redeploy after adding variables: `vercel --prod`

### Cold start issues
- First request after inactivity may be slow
- Consider using Vercel Pro for better performance
- Or use a keep-alive service

## Cost Considerations

- **Vercel Hobby**: Free tier available
- **Vercel Pro**: $20/month for better limits
- **Neo4j Aura**: Free tier available
- **OpenAI/Gemini**: Pay per use

## Next Steps

1. Deploy to Vercel
2. Test the endpoints
3. Update your agent system to use the Vercel URL
4. Monitor usage and costs

