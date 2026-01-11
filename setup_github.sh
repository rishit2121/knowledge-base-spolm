#!/bin/bash

# Script to create GitHub repo and push code

set -e

echo "🚀 Setting up GitHub repository"
echo ""

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "Initializing git repository..."
    git init
    echo "✓ Git initialized"
else
    echo "✓ Git already initialized"
fi

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo ""
    echo "⚠️  GitHub CLI (gh) is not installed."
    echo "   Install it with: brew install gh"
    echo "   Or create repo manually at: https://github.com/new"
    echo ""
    read -p "Do you want to continue with manual setup? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
    
    echo ""
    echo "Manual setup:"
    echo "1. Go to https://github.com/new"
    echo "2. Create a new repository (don't initialize with README)"
    echo "3. Copy the repository URL"
    echo "4. Run: git remote add origin <your-repo-url>"
    echo "5. Run: git push -u origin main"
    exit 0
fi

# Check if logged in to GitHub
if ! gh auth status &> /dev/null; then
    echo "Logging in to GitHub..."
    gh auth login
fi

# Get repository name
echo ""
read -p "Enter GitHub repository name (default: knowledge-base-spolm): " repo_name
repo_name=${repo_name:-knowledge-base-spolm}

# Get repository description
read -p "Enter repository description (optional): " repo_description

# Create .gitignore if it doesn't exist
if [ ! -f ".gitignore" ]; then
    echo ""
    echo "Creating .gitignore..."
    cat > .gitignore << 'EOF'
# Environment
.env
.venv
venv/
env/

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Logs
*.log
logs/

# OS
.DS_Store
Thumbs.db

# Vercel
.vercel
EOF
    echo "✓ .gitignore created"
fi

# Add all files
echo ""
echo "Staging files..."
git add .
echo "✓ Files staged"

# Check if there are changes
if git diff --staged --quiet; then
    echo "⚠️  No changes to commit"
else
    # Commit
    echo ""
    read -p "Enter commit message (default: Initial commit): " commit_msg
    commit_msg=${commit_msg:-Initial commit}
    
    git commit -m "$commit_msg"
    echo "✓ Changes committed"
fi

# Create GitHub repository
echo ""
echo "Creating GitHub repository: $repo_name"
if [ -z "$repo_description" ]; then
    gh repo create "$repo_name" --public --source=. --remote=origin --push
else
    gh repo create "$repo_name" --public --description "$repo_description" --source=. --remote=origin --push
fi

echo ""
echo "✅ Repository created and pushed to GitHub!"
echo ""
echo "Repository URL: https://github.com/$(gh api user --jq .login)/$repo_name"
echo ""
echo "Next steps:"
echo "1. Go to https://vercel.com/new"
echo "2. Import your GitHub repository"
echo "3. Add environment variables in Vercel"
echo "4. Deploy!"
echo ""

