"""Models for retrieval requests and responses."""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class RetrievalRequest(BaseModel):
    """Request for memory retrieval."""
    task_text: str
    agent_id: Optional[str] = None
    context: Optional[str] = None
    top_k: int = 5


class RelatedRun(BaseModel):
    """Information about a related run."""
    run_id: str
    agent_id: str
    summary: str
    outcome: str
    run_tree: Optional[Dict[str, Any]] = None  # Full run tree/map for detailed retrieval
    references: List[Dict[str, Any]]
    artifacts: List[Dict[str, Any]]
    similarity_score: float


class RetrievalResponse(BaseModel):
    """Response from memory retrieval."""
    observations: List[str]
    related_runs: List[RelatedRun]
    confidence: float
    query_embedding: Optional[List[float]] = None


class RunDetail(BaseModel):
    """Detailed information about a run."""
    run_id: str
    agent_id: Optional[str]
    summary: str
    outcome: str
    run_tree: Optional[Dict[str, Any]] = None
    references: List[Dict[str, Any]]
    artifacts: List[Dict[str, Any]]
    created_at: Optional[str] = None


class RetrieveAllResponse(BaseModel):
    """Response from retrieve_all endpoint."""
    runs: List[RunDetail]
    total_count: int

