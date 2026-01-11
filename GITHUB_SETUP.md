# Setting Up GitHub Repository

## Option 1: Automated Script (Recommended)

Run the setup script:

```bash
./setup_github.sh
```

This will:
1. Initialize git (if not already)
2. Create `.gitignore` (if needed)
3. Stage and commit files
4. Create GitHub repo using `gh` CLI
5. Push code to GitHub

**Requirements:**
- GitHub CLI installed: `brew install gh`
- Logged in: `gh auth login`

## Option 2: Manual Setup

### Step 1: Initialize Git

```bash
git init
git add .
git commit -m "Initial commit: Knowledge Base for Agent Memory"
```

### Step 2: Create GitHub Repository

**Via GitHub Website:**
1. Go to https://github.com/new
2. Repository name: `knowledge-base-spolm` (or your choice)
3. Description: "Run-centric knowledge base for agentic workflow memory"
4. Choose Public or Private
5. **Don't** initialize with README, .gitignore, or license
6. Click "Create repository"

### Step 3: Connect and Push

```bash
# Add remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/knowledge-base-spolm.git

# Or if you prefer SSH:
# git remote add origin git@github.com:YOUR_USERNAME/knowledge-base-spolm.git

# Push to GitHub
git branch -M main
git push -u origin main
```

## Option 3: Using GitHub CLI

If you have `gh` CLI installed:

```bash
# Login (if not already)
gh auth login

# Create repo and push
gh repo create knowledge-base-spolm --public --source=. --remote=origin --push
```

## After Pushing to GitHub

### Deploy to Vercel from GitHub

1. **Go to Vercel**: https://vercel.com/new
2. **Import Git Repository**: 
   - Click "Import Git Repository"
   - Select your GitHub repository
3. **Configure Project**:
   - Framework Preset: Other (or leave default)
   - Root Directory: `./` (default)
4. **Environment Variables**:
   - Add all your environment variables:
     - `NEO4J_URI`
     - `NEO4J_USER`
     - `NEO4J_PASSWORD`
     - `PROVIDER`
     - `OPENAI_API_KEY` or `GEMINI_API_KEY`
5. **Deploy**: Click "Deploy"

### Automatic Deployments

After the first deployment:
- Every push to `main` → Production deployment
- Every pull request → Preview deployment
- Environment variables are shared across deployments

## Verify Deployment

After deployment, test your API:

```bash
# Get your Vercel URL (shown after deployment)
curl https://your-project.vercel.app/

# Test stats
curl https://your-project.vercel.app/stats
```

## Update Your Test Script

Update `test_add_and_retrieve.py` to use your Vercel URL:

```python
# In the main() function, change:
api_url = "https://your-project.vercel.app"
```

Or pass it as argument:
```bash
python test_add_and_retrieve.py https://your-project.vercel.app
```

## Troubleshooting

### "Repository already exists"
- The repo name is taken, choose a different name
- Or delete the existing repo first

### "gh: command not found"
- Install GitHub CLI: `brew install gh`
- Or use manual setup (Option 2)

### "Authentication failed"
- Run: `gh auth login`
- Follow the prompts

### "Permission denied"
- Make sure you have write access to the repository
- Check your GitHub authentication

