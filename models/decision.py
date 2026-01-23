"""Models for memory decision layer."""
from typing import Literal, Optional
from pydantic import BaseModel
from datetime import datetime


class MemoryDecision(BaseModel):
    """Decision made by the memory admission control system."""
    run_id: str
    decision: Literal["ADD", "NOT", "REPLACE", "MERGE"]
    target_run_id: Optional[str] = None  # For REPLACE and MERGE
    reason: str
    similarity_score: Optional[float] = None
    similar_runs: Optional[list[dict]] = None  # List of similar runs that influenced the decision
    timestamp: datetime


class SimilarRun(BaseModel):
    """A similar run found during decision making."""
    run_id: str
    summary: str
    outcome: str
    similarity: float
    references: list[dict]
    artifacts: list[dict]

