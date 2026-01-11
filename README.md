# Knowledge Base for Agentic Workflow Runs

A run-centric knowledge base system that stores and retrieves agent workflow experiences using Neo4j as the graph database backend.

## Overview

This system implements a complete knowledge base infrastructure for storing agent runs with:
- **Neo4j Knowledge Graph**: Stores runs, tasks, references, artifacts, and outcomes
- **Memory Builder**: Processes completed runs and extracts structured information
- **Memory Retrieval API**: Provides similarity search and context retrieval for agents
- **Vector Embeddings**: Uses OpenAI embeddings for semantic similarity

## Architecture

```
[Run Logs] 
    ↓
[Memory Builder]        ← Processes runs, extracts knowledge
    ↓
[Neo4j Knowledge Graph] ← Stores structured experience
    ↓
[Memory Retrieval API]  ← Retrieves relevant context
```

## Prerequisites

Before setting up, ensure you have:

1. **Python 3.9+** installed
2. **Neo4j** running (choose one):
   - Neo4j Aura (cloud, recommended)
   - Self-hosted Neo4j (Docker or local installation)
3. **OpenAI API Key** for embeddings and summarization
4. **Docker** (optional, for local Neo4j)

## Quick Start

### 1. Clone and Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

Copy the example environment file and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env` with your settings:

```env
# Neo4j Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password_here

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Optional: Adjust these if needed
EMBEDDING_MODEL=text-embedding-3-small
SIMILARITY_THRESHOLD=0.85
```

### 3. Start Neo4j (if using Docker)

```bash
# Update password in docker-compose.yml first!
docker-compose up -d
```

Or use Neo4j Aura and update `NEO4J_URI` in `.env` to your Aura connection string.

### 4. Initialize Database Schema

```bash
python init_db.py
```

This will:
- Create vector indexes (if supported)
- Set up node labels and relationships
- Create constraints for data integrity

### 5. Start the API Server

```bash
python api.py
```

The API will be available at `http://localhost:8000`

API documentation: `http://localhost:8000/docs`

## Usage

### Processing a Run (Write Path)

When an agent run completes, send it to the knowledge base:

```python
from models.run import RunPayload
from memory_builder import MemoryBuilder
from datetime import datetime

builder = MemoryBuilder()

payload = RunPayload(
    run_id="run_001",
    task_text="Create user authentication system",
    agent_id="agent_001",
    run_tree={
        "steps": [...],
        "reasoning": "...",
        "tools_used": [...]
    },
    outcome="success",
    created_at=datetime.utcnow()
)

result = builder.process_run(payload)
```

Or via HTTP API:

```bash
curl -X POST "http://localhost:8000/runs" \
  -H "Content-Type: application/json" \
  -d '{
    "run_id": "run_001",
    "task_text": "Create user authentication system",
    "agent_id": "agent_001",
    "run_tree": {...},
    "outcome": "success"
  }'
```

### Retrieving Memory (Read Path)

Before starting a task, agents can retrieve relevant context:

```python
from models.retrieval import RetrievalRequest
from memory_retrieval import MemoryRetrieval

retrieval = MemoryRetrieval()

request = RetrievalRequest(
    task_text="I need to implement user authentication",
    agent_id="agent_001",
    top_k=5
)

response = retrieval.retrieve(request)

print(f"Confidence: {response.confidence}")
print(f"Observations: {response.observations}")
print(f"Related Runs: {len(response.related_runs)}")
```

Or via HTTP API:

```bash
curl -X POST "http://localhost:8000/retrieve" \
  -H "Content-Type: application/json" \
  -d '{
    "task_text": "I need to implement user authentication",
    "agent_id": "agent_001",
    "top_k": 5
  }'
```

## Graph Schema

### Node Labels

- **:Task** - Represents tasks that trigger runs
  - `id`, `text`, `embedding`
  
- **:Run** - Represents completed agent runs
  - `id`, `agent_id`, `summary`, `embedding`, `created_at`
  
- **:Reference** - Information referenced during runs
  - `id`, `type`, `embedding`, `source_ref`
  
- **:Artifact** - Outputs produced during runs
  - `id`, `type`, `embedding`, `hash`
  
- **:Outcome** - Run outcomes
  - `label` (success/failure/partial)

### Relationships

- `(:Task)-[:TRIGGERED]->(:Run)`
- `(:Run)-[:READS]->(:Reference)`
- `(:Run)-[:WRITES]->(:Artifact)`
- `(:Run)-[:ENDED_WITH]->(:Outcome)`

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NEO4J_URI` | Neo4j connection URI | `bolt://localhost:7687` |
| `NEO4J_USER` | Neo4j username | `neo4j` |
| `NEO4J_PASSWORD` | Neo4j password | (required) |
| `OPENAI_API_KEY` | OpenAI API key | (required) |
| `EMBEDDING_MODEL` | Embedding model name | `text-embedding-3-small` |
| `EMBEDDING_DIMENSION` | Embedding vector dimension | `1536` |
| `SIMILARITY_THRESHOLD` | Minimum similarity for task matching | `0.85` |
| `API_HOST` | API server host | `0.0.0.0` |
| `API_PORT` | API server port | `8000` |

## Development

### Project Structure

```
knowledge_base_SPOLM/
├── api.py                 # FastAPI application
├── memory_builder.py      # Write path - processes runs
├── memory_retrieval.py    # Read path - retrieves context
├── config.py              # Configuration management
├── init_db.py             # Database initialization
├── example_usage.py       # Example usage scripts
├── db/
│   ├── connection.py      # Neo4j connection
│   └── schema.py          # Schema definition
├── models/
│   ├── run.py             # Run data models
│   └── retrieval.py       # Retrieval models
└── services/
    ├── embedding.py       # Embedding service
    └── llm.py             # LLM service
```

### Running Examples

```bash
python example_usage.py
```

### API Endpoints

- `GET /` - Health check
- `POST /runs` - Process a completed run
- `POST /retrieve` - Retrieve relevant memory
- `GET /stats` - Get knowledge base statistics
- `GET /docs` - Interactive API documentation

## Neo4j Setup Options

### Option 1: Neo4j Aura (Recommended)

1. Sign up at [neo4j.com/cloud/aura](https://neo4j.com/cloud/aura)
2. Create a free instance
3. Copy the connection URI and credentials
4. Update `.env` with your Aura credentials

### Option 2: Docker (Local Development)

```bash
# Edit docker-compose.yml to set your password
docker-compose up -d
```

### Option 3: Local Installation

1. Download Neo4j from [neo4j.com/download](https://neo4j.com/download)
2. Install and start Neo4j
3. Set initial password
4. Update `.env` with connection details

## Vector Index Support

This system uses vector indexes for efficient similarity search. Vector indexes are available in:
- **Neo4j 5.11+** (community/enterprise)
- **Neo4j Aura** (all versions)

If vector indexes are not available, the system falls back to:
- Manual cosine similarity calculation
- Regular indexes for node lookups

The system will automatically detect and use the best available method.

## Integration Guide

### Integrating with Your Agent System

1. **After Run Completion**: Call `POST /runs` with the run payload
2. **Before Task Start**: Call `POST /retrieve` to get relevant context
3. **Use Observations**: Feed the observations to your agent as context

### Example Integration

```python
# After agent run completes
def on_run_complete(run_data):
    payload = RunPayload(
        run_id=run_data["id"],
        task_text=run_data["task"],
        agent_id=run_data["agent_id"],
        run_tree=run_data["tree"],
        outcome=run_data["outcome"]
    )
    
    response = requests.post("http://localhost:8000/runs", json=payload.dict())
    return response.json()

# Before agent starts task
def get_context_for_task(task_text, agent_id):
    request = RetrievalRequest(
        task_text=task_text,
        agent_id=agent_id,
        top_k=5
    )
    
    response = requests.post("http://localhost:8000/retrieve", json=request.dict())
    return response.json()
```

## Monitoring and Metrics

### Check Knowledge Base Stats

```bash
curl http://localhost:8000/stats
```

Returns counts of nodes and relationships in the graph.

### Metrics to Track

- **Retrieval Relevance**: How often retrieved runs are actually useful
- **Agent Success Rate**: Compare success rates with/without memory
- **Memory Hit Rate**: How often similar runs are found
- **Repeated Failures**: Identify patterns in failures

## Troubleshooting

### Neo4j Connection Issues

- Verify Neo4j is running: `docker ps` or check Aura dashboard
- Test connection: `cypher-shell -u neo4j -p password`
- Check firewall/network settings

### Vector Index Errors

- Ensure Neo4j 5.11+ or Aura
- Check that GDS library is installed (for similarity functions)
- System will fallback to manual calculation if needed

### OpenAI API Issues

- Verify API key is correct
- Check API quota/rate limits
- Ensure you have access to embedding models

## Production Considerations

1. **Scaling**: Consider connection pooling for high throughput
2. **Error Handling**: Add retry logic for API calls
3. **Monitoring**: Set up logging and metrics collection
4. **Backup**: Regular Neo4j backups
5. **Security**: Use environment variables, never commit secrets
6. **Rate Limiting**: Add rate limiting to API endpoints

## License

This project is provided as-is for building agent knowledge bases.

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review Neo4j and OpenAI documentation
3. Verify your configuration matches the examples

---

**Remember**: The graph stores experience, not decisions. Retrieval finds relevance, not truth. Agents remain autonomous.

