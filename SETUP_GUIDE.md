# Setup Guide - Knowledge Base Infrastructure

## ✅ What Has Been Created

Your knowledge base infrastructure is now set up with the following components:

### Core Components

1. **Neo4j Knowledge Graph** (`db/schema.py`)
   - Graph schema with nodes: Task, Run, Reference, Artifact, Outcome
   - Relationships: TRIGGERED, READS, WRITES, ENDED_WITH
   - Vector indexes for similarity search
   - Constraints for data integrity

2. **Memory Builder** (`memory_builder.py`)
   - Processes completed agent runs
   - Extracts tasks, references, and artifacts
   - Generates run summaries using LLM
   - Stores everything in Neo4j

3. **Memory Retrieval API** (`memory_retrieval.py`)
   - Vector similarity search
   - Graph expansion for context
   - Pattern analysis
   - Confidence scoring

4. **FastAPI Application** (`api.py`)
   - RESTful API endpoints
   - Health checks
   - Statistics endpoint

### Supporting Infrastructure

- **Configuration Management** (`config.py`)
- **Database Connection** (`db/connection.py`)
- **Embedding Service** (`services/embedding.py`) - OpenAI embeddings
- **LLM Service** (`services/llm.py`) - Run summarization
- **Data Models** (`models/`) - Pydantic models
- **Docker Compose** (`docker-compose.yml`) - Local Neo4j setup
- **Initialization Script** (`init_db.py`) - Schema setup
- **Example Usage** (`example_usage.py`) - Usage examples

## 🔧 What You Need to Set Up

### 1. Neo4j Database

**Option A: Neo4j Aura (Recommended for Production)**
1. Sign up at https://neo4j.com/cloud/aura
2. Create a free instance
3. Copy the connection URI (format: `neo4j+s://xxx.databases.neo4j.io`)
4. Get your username and password

**Option B: Docker (Local Development)**
1. Edit `docker-compose.yml` and set your password:
   ```yaml
   NEO4J_AUTH=neo4j/your_password_here
   ```
2. Start Neo4j:
   ```bash
   docker-compose up -d
   ```
3. Access Neo4j Browser at http://localhost:7474

**Option C: Local Installation**
1. Download from https://neo4j.com/download
2. Install and start Neo4j
3. Set initial password

### 2. OpenAI API Key

1. Get an API key from https://platform.openai.com/api-keys
2. Ensure you have access to:
   - Embedding models (e.g., `text-embedding-3-small`)
   - Chat models (e.g., `gpt-4-turbo-preview`)

### 3. Environment Configuration

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your credentials:
   ```env
   # Neo4j (choose based on your setup)
   NEO4J_URI=bolt://localhost:7687          # For local/Docker
   # NEO4J_URI=neo4j+s://xxx.databases.neo4j.io  # For Aura
   NEO4J_USER=neo4j
   NEO4J_PASSWORD=your_neo4j_password
   
   # OpenAI
   OPENAI_API_KEY=sk-your-api-key-here
   ```

### 4. Install Dependencies

```bash
# Option 1: Use setup script
./setup.sh

# Option 2: Manual setup
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 5. Initialize Database

```bash
python init_db.py
```

This will:
- Connect to Neo4j
- Create vector indexes
- Set up constraints
- Verify schema

### 6. Start the API

```bash
python api.py
```

Or with uvicorn directly:
```bash
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

## 🧪 Testing the Setup

### 1. Test Database Connection

```bash
python -c "from db.connection import get_neo4j_driver; driver = get_neo4j_driver(); print('✓ Connected!')"
```

### 2. Test API

```bash
# Health check
curl http://localhost:8000/

# Get stats
curl http://localhost:8000/stats
```

### 3. Run Example

```bash
python example_usage.py
```

## 📋 Integration Checklist

- [ ] Neo4j is running and accessible
- [ ] `.env` file is configured with credentials
- [ ] Dependencies are installed
- [ ] Database schema is initialized (`init_db.py` completed successfully)
- [ ] API server starts without errors
- [ ] Can connect to Neo4j from Python
- [ ] OpenAI API key is valid and has quota

## 🔗 Connecting Your Agent System

### Write Path (After Run Completion)

```python
import requests
from datetime import datetime

def store_run(run_id, task_text, agent_id, run_tree, outcome):
    """Store a completed run in the knowledge base."""
    payload = {
        "run_id": run_id,
        "task_text": task_text,
        "agent_id": agent_id,
        "run_tree": run_tree,
        "outcome": outcome,
        "created_at": datetime.utcnow().isoformat()
    }
    
    response = requests.post(
        "http://localhost:8000/runs",
        json=payload
    )
    return response.json()
```

### Read Path (Before Task Start)

```python
def get_context(task_text, agent_id=None):
    """Retrieve relevant context for a task."""
    payload = {
        "task_text": task_text,
        "agent_id": agent_id,
        "top_k": 5
    }
    
    response = requests.post(
        "http://localhost:8000/retrieve",
        json=payload
    )
    return response.json()
```

## 🚨 Troubleshooting

### "Connection refused" to Neo4j
- Check Neo4j is running: `docker ps` or check Aura dashboard
- Verify `NEO4J_URI` in `.env` matches your setup
- Test connection: `cypher-shell -u neo4j -p password`

### "Vector index not supported"
- This is OK! The system falls back to manual similarity calculation
- For better performance, use Neo4j 5.11+ or Aura

### "OpenAI API error"
- Verify API key is correct
- Check you have quota/credits
- Ensure model names are correct

### Import errors
- Make sure virtual environment is activated
- Run `pip install -r requirements.txt` again
- Check Python version (3.9+)

## 📊 Next Steps

1. **Start Processing Runs**: Integrate the write path into your agent system
2. **Test Retrieval**: Query the knowledge base before tasks
3. **Monitor Performance**: Use `/stats` endpoint to track growth
4. **Tune Parameters**: Adjust `SIMILARITY_THRESHOLD` based on results
5. **Scale**: Consider connection pooling for high throughput

## 🎯 Key Features

✅ **Run-centric memory** - Stores complete run experiences  
✅ **Vector similarity search** - Finds relevant past runs  
✅ **Graph expansion** - Retrieves full context (references, artifacts)  
✅ **Pattern analysis** - Identifies success/failure patterns  
✅ **Confidence scoring** - Indicates retrieval quality  
✅ **Async-ready** - Can be called asynchronously after run completion  

## 📚 Documentation

- Full README: `README.md`
- API docs: http://localhost:8000/docs (when server is running)
- Example usage: `example_usage.py`

---

**You're all set!** The infrastructure is ready. Just configure your credentials and start processing runs.

