"""FastAPI application for the Memory Retrieval API."""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from models.run import RunPayload
from models.retrieval import RetrievalRequest, RetrievalResponse, RetrieveAllResponse, RunDetail
from memory_builder import MemoryBuilder
from memory_retrieval import MemoryRetrieval
from db.connection import close_neo4j_driver
import config
from typing import Optional


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown."""
    # Startup
    config.Config.validate()
    yield
    # Shutdown
    close_neo4j_driver()


app = FastAPI(
    title="Knowledge Base API",
    description="Run-centric knowledge base for agent memory",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services (lazy initialization for Vercel)
memory_builder = None
memory_retrieval = None

def get_memory_builder():
    """Lazy initialization of memory builder."""
    global memory_builder
    if memory_builder is None:
        memory_builder = MemoryBuilder()
    return memory_builder

def get_memory_retrieval():
    """Lazy initialization of memory retrieval."""
    global memory_retrieval
    if memory_retrieval is None:
        memory_retrieval = MemoryRetrieval()
    return memory_retrieval


@app.get("/")
async def root():
    """Health check endpoint."""
    # Debug: Show Neo4j URI (masked for security)
    neo4j_uri = config.Config.NEO4J_URI
    # Mask the instance ID for security
    if "databases.neo4j.io" in neo4j_uri:
        parts = neo4j_uri.split("databases.neo4j.io")
        masked_uri = "neo4j+s://*****.databases.neo4j.io" if parts[0].startswith("neo4j+s://") else "neo4j://*****.databases.neo4j.io"
    else:
        masked_uri = neo4j_uri.split("@")[-1] if "@" in neo4j_uri else "localhost"
    
    return {
        "status": "healthy",
        "service": "Knowledge Base API",
        "version": "1.0.0",
        "neo4j_uri_format": masked_uri,
        "neo4j_user": config.Config.NEO4J_USER
    }


@app.post("/runs", response_model=dict)
async def process_run(payload: RunPayload):
    """
    Process a completed run and store it in the knowledge graph.
    
    This is the write path - called when an agent run completes.
    """
    try:
        builder = get_memory_builder()
        result = builder.process_run(payload)
        
        if result.get("success"):
            return {
                "status": "success",
                "message": "Run processed and stored successfully",
                "data": result
            }
        else:
            error_msg = result.get('error', 'Unknown error')
            # Log the actual error for debugging
            print(f"[ERROR] process_run returned success=False: {error_msg}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to process run: {error_msg}"
            )
    except HTTPException:
        # Re-raise HTTPExceptions as-is (don't double-wrap)
        raise
    except Exception as e:
        import traceback
        # Log the full error for debugging
        print(f"[ERROR] Exception in process_run endpoint:")
        print(traceback.format_exc())
        error_detail = f"{str(e)}\n\nTraceback:\n{traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_detail)


@app.post("/retrieve", response_model=RetrievalResponse)
async def retrieve_memory(request: RetrievalRequest):
    """
    Retrieve relevant memory for a given task.
    
    This is the read path - called by agents before starting a task.
    """
    try:
        retrieval = get_memory_retrieval()
        response = retrieval.retrieve(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/retrieve_all", response_model=RetrieveAllResponse)
async def retrieve_all_runs(user_id: Optional[str] = None, agent_id: Optional[str] = None, limit: Optional[int] = None):
    """
    Retrieve all runs from the knowledge graph.
    
    Args:
        user_id: Optional filter by user ID
        agent_id: Optional filter by agent ID
        limit: Optional limit on number of runs to return
        
    Returns:
        All runs with their full details
    """
    try:
        retrieval = get_memory_retrieval()
        runs_data = retrieval.retrieve_all(user_id=user_id, agent_id=agent_id, limit=limit)
        
        # Convert to RunDetail models
        runs = [
            RunDetail(
                run_id=run["run_id"],
                user_id=run.get("user_id"),
                agent_id=run["agent_id"],
                summary=run["summary"],
                reason_added=run.get("reason_added"),
                outcome=run["outcome"],
                run_tree=run["run_tree"],
                references=run["references"],
                artifacts=run["artifacts"],
                created_at=run["created_at"]
            )
            for run in runs_data
        ]
        
        return RetrieveAllResponse(
            runs=runs,
            total_count=len(runs)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
async def get_stats():
    """Get statistics about the knowledge base."""
    from db.connection import get_neo4j_driver
    
    driver = get_neo4j_driver()
    with driver.session() as session:
        stats = {}
        
        # Count nodes
        for label in ["Task", "Run", "Reference", "Artifact", "Outcome"]:
            result = session.run(f"MATCH (n:{label}) RETURN count(n) AS count")
            stats[label.lower() + "_count"] = result.single()["count"]
        
        # Count relationships
        result = session.run("""
            MATCH ()-[r]->()
            RETURN type(r) AS type, count(r) AS count
        """)
        relationship_counts = {}
        for record in result:
            relationship_counts[record["type"]] = record["count"]
        stats["relationships"] = relationship_counts
        
        return stats


# Vercel serverless function handler
# Vercel will automatically detect the 'app' variable
__all__ = ["app"]

# Only run uvicorn if not in Vercel environment
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api:app",
        host=config.Config.API_HOST,
        port=config.Config.API_PORT,
        reload=True
    )

