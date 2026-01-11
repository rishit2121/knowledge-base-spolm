#!/bin/bash

# Setup script for Knowledge Base system

set -e

echo "🚀 Setting up Knowledge Base for Agentic Workflow Runs"
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python $python_version found"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo ""
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✓ Dependencies installed"

# Check for .env file
if [ ! -f ".env" ]; then
    echo ""
    echo "⚠ .env file not found. Creating from template..."
    cp .env.example .env
    echo "✓ .env file created"
    echo ""
    echo "⚠ IMPORTANT: Please edit .env and set:"
    echo "   - NEO4J_PASSWORD"
    echo "   - OPENAI_API_KEY"
    echo ""
else
    echo "✓ .env file exists"
fi

# Check Neo4j connection
echo ""
echo "Checking Neo4j connection..."
if python3 -c "import config; config.Config.validate()" 2>/dev/null; then
    echo "✓ Configuration valid"
else
    echo "⚠ Configuration incomplete - please check .env file"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Edit .env file with your credentials"
echo "  2. Start Neo4j (docker-compose up -d or use Aura)"
echo "  3. Run: python init_db.py"
echo "  4. Start API: python api.py"
echo ""

