# Quick GitHub Setup Commands

Run these commands in order:

## Step 1: Initialize Git
```bash
git init
git add .
git commit -m "Initial commit: Knowledge Base for Agent Memory"
```

## Step 2: Create GitHub Repo and Push
```bash
# Make sure you're logged in
gh auth login

# Create repo and push (change name if needed)
gh repo create knowledge-base-spolm --public --source=. --remote=origin --push
```

## Step 3: Verify
```bash
# Check your repo
gh repo view --web
```

## Step 4: Deploy to Vercel
1. Go to: https://vercel.com/new
2. Import your GitHub repository
3. Add environment variables
4. Deploy!

Done! 🎉

