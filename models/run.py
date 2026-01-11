"""Models for run data."""
from typing import Dict, Any, Optional, Literal, List
from pydantic import BaseModel
from datetime import datetime


class RunPayload(BaseModel):
    """Input payload for processing a completed run.
    
    Supports two formats:
    1. New format (structured run log):
       - id, run_id, start_timestamp, agent_id, user_task, metadata, steps, etc.
    2. Old format (backward compatible):
       - run_id, task_text, agent_id, run_tree, outcome, created_at
    """
    # New format fields
    id: Optional[str] = None
    run_id: str
    start_timestamp: Optional[str] = None
    agent_id: str
    user_task: Optional[str] = None  # New format
    metadata: Optional[Dict[str, Any]] = None
    steps: Optional[List[Dict[str, Any]]] = None
    final_output: Optional[str] = None
    duration: Optional[int] = None
    status: Optional[str] = None  # "complete", "success", "failure", etc.
    agent_prompt: Optional[str] = None
    end_timestamp: Optional[str] = None
    
    # Old format fields (for backward compatibility)
    task_text: Optional[str] = None
    run_tree: Optional[Dict[str, Any]] = None
    outcome: Optional[Literal["success", "failure", "partial"]] = None
    created_at: Optional[datetime] = None
    
    def get_task_text(self) -> str:
        """Get task text from user_task or task_text."""
        return self.user_task or self.task_text or ""
    
    def get_run_tree(self) -> Dict[str, Any]:
        """Get the full run log as a dictionary."""
        # If run_tree is provided (old format), use it
        if self.run_tree:
            return self.run_tree
        
        # Otherwise, construct from new format fields
        return {
            "id": self.id,
            "run_id": self.run_id,
            "start_timestamp": self.start_timestamp,
            "agent_id": self.agent_id,
            "user_task": self.user_task,
            "metadata": self.metadata,
            "steps": self.steps or [],
            "final_output": self.final_output,
            "duration": self.duration,
            "status": self.status,
            "agent_prompt": self.agent_prompt,
            "end_timestamp": self.end_timestamp
        }
    
    def get_outcome(self) -> str:
        """Get outcome from status or outcome field."""
        if self.outcome:
            return self.outcome
        
        if self.status:
            status_lower = self.status.lower()
            if status_lower in ["complete", "success"]:
                return "success"
            elif status_lower == "failure":
                return "failure"
            else:
                return "partial"
        
        return "partial"  # Default
    
    def get_created_at(self) -> Optional[datetime]:
        """Get created_at from start_timestamp or created_at field."""
        if self.created_at:
            return self.created_at
        
        if self.start_timestamp:
            try:
                from dateutil import parser
                return parser.isoparse(self.start_timestamp)
            except:
                pass
        
        return None


class RunSummary(BaseModel):
    """Summary of a run for storage."""
    run_id: str
    agent_id: str
    summary: str
    embedding: list[float]
    created_at: datetime


class Reference(BaseModel):
    """A reference that was read during a run."""
    id: str
    type: str  # e.g., "schema", "document", "api_response", "prior_run"
    embedding: list[float]
    source_ref: str


class Artifact(BaseModel):
    """An artifact that was produced during a run."""
    id: str
    type: str  # e.g., "schema", "plan", "report", "code"
    embedding: list[float]
    hash: str


class Outcome(BaseModel):
    """Outcome of a run."""
    label: Literal["success", "failure", "partial"]

