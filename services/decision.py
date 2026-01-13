"""Memory Decision Layer - decides whether to add, skip, replace, or merge runs."""
from typing import Dict, Any, List, Optional, Literal
import json
import re
from datetime import datetime, timezone
import numpy as np
from neo4j import Driver

from db.connection import get_neo4j_driver
from models.decision import MemoryDecision, SimilarRun
from services.embedding import EmbeddingService
from services.llm import LLMService
import config


class DecisionLayer:
    """
    Decision layer for memory admission control.
    
    Implements two-stage decision:
    1. Deterministic pre-filter (cheap rules)
    2. LLM judge (for ambiguous cases)
    """
    
    # Thresholds for deterministic decisions
    LOW_SIMILARITY_THRESHOLD = 0.7
    VERY_HIGH_SIMILARITY_THRESHOLD = 0.95
    
    def __init__(self):
        self.driver = get_neo4j_driver()
        self.embedding_service = EmbeddingService()
        self.llm_service = LLMService()
        self.similarity_threshold = config.Config.SIMILARITY_THRESHOLD
    
    def decide(
        self,
        run_id: str,
        run_summary: str,
        run_embedding: List[float],
        task_text: str,
        outcome: str,
        references: List[Dict[str, Any]],
        artifacts: List[Dict[str, Any]]
    ) -> MemoryDecision:
        """
        Decide what to do with a new run.
        
        Returns:
            MemoryDecision with decision, target_run_id (if REPLACE/MERGE), and reason
        """
        # Stage 1: Find similar runs
        similar_runs = self._find_similar_runs(run_embedding, top_k=3)
        
        # Stage 2: Deterministic pre-filter
        deterministic_decision = self._deterministic_filter(similar_runs)
        if deterministic_decision:
            deterministic_decision.run_id = run_id
            return deterministic_decision
        
        # Stage 3: LLM judge for ambiguous cases
        decision = self._llm_judge(
            run_summary=run_summary,
            task_text=task_text,
            outcome=outcome,
            references=references,
            artifacts=artifacts,
            similar_runs=similar_runs
        )
        decision.run_id = run_id
        return decision
    
    def _find_similar_runs(
        self,
        run_embedding: List[float],
        top_k: int = 3
    ) -> List[SimilarRun]:
        """Find similar runs using vector search."""
        with self.driver.session() as session:
            # Get all active runs (exclude superseded)
            result = session.run("""
                MATCH (r:Run)
                WHERE r.embedding IS NOT NULL
                  AND (r.status IS NULL OR r.status = 'active')
                RETURN r.id AS run_id,
                       r.summary AS summary,
                       r.embedding AS embedding
            """)
            
            expected_dim = len(run_embedding)
            runs_with_similarity = []
            for record in result:
                existing_embedding = record["embedding"]
                # Skip embeddings with wrong dimension (from different model)
                if len(existing_embedding) != expected_dim:
                    continue
                try:
                    similarity = self._cosine_similarity(run_embedding, existing_embedding)
                except Exception as e:
                    # Skip if similarity calculation fails
                    continue
                
                if similarity >= self.LOW_SIMILARITY_THRESHOLD:
                    # Get outcome and relationships
                    run_id = record["run_id"]
                    run_details = self._get_run_details(run_id)
                    
                    runs_with_similarity.append(SimilarRun(
                        run_id=run_id,
                        summary=record["summary"],
                        outcome=run_details.get("outcome", "unknown"),
                        similarity=similarity,
                        references=run_details.get("references", []),
                        artifacts=run_details.get("artifacts", [])
                    ))
            
            # Sort by similarity and return top_k
            runs_with_similarity.sort(key=lambda x: x.similarity, reverse=True)
            return runs_with_similarity[:top_k]
    
    def _get_run_details(self, run_id: str) -> Dict[str, Any]:
        """Get full details of a run including references and artifacts."""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (r:Run {id: $run_id})
                OPTIONAL MATCH (r)-[:READS]->(ref:Reference)
                OPTIONAL MATCH (r)-[:WRITES]->(a:Artifact)
                OPTIONAL MATCH (r)-[:ENDED_WITH]->(o:Outcome)
                RETURN collect(DISTINCT {
                    id: ref.id,
                    type: ref.type
                }) AS references,
                collect(DISTINCT {
                    id: a.id,
                    type: a.type
                }) AS artifacts,
                o.label AS outcome
            """, run_id=run_id)
            
            record = result.single()
            if not record:
                return {"outcome": "unknown", "references": [], "artifacts": []}
            
            return {
                "outcome": record["outcome"] or "unknown",
                "references": [r for r in (record["references"] or []) if r.get("id")],
                "artifacts": [a for a in (record["artifacts"] or []) if a.get("id")]
            }
    
    def _deterministic_filter(
        self,
        similar_runs: List[SimilarRun]
    ) -> Optional[MemoryDecision]:
        """
        Stage 1: Deterministic pre-filter.
        Returns decision if clear-cut, None if needs LLM judge.
        """
        # Rule 1: No similar runs found -> ADD
        if not similar_runs:
            return MemoryDecision(
                run_id="",  # Will be set by caller
                decision="ADD",
                reason="No similar runs found in memory",
                similarity_score=None,
                timestamp=datetime.now(timezone.utc)
            )
        
        best_match = similar_runs[0]
        
        # Rule 2: Very low similarity -> ADD
        if best_match.similarity < self.LOW_SIMILARITY_THRESHOLD:
            return MemoryDecision(
                run_id="",
                decision="ADD",
                reason=f"Similarity ({best_match.similarity:.2f}) below threshold ({self.LOW_SIMILARITY_THRESHOLD})",
                similarity_score=best_match.similarity,
                timestamp=datetime.now(timezone.utc)
            )
        
        # Rule 3: Very high similarity + same structure -> MERGE (let LLM decide which is canonical)
        if best_match.similarity > self.VERY_HIGH_SIMILARITY_THRESHOLD:
            # Check if structure is similar (same number of references/artifacts)
            # This is a simple heuristic - LLM will make final call
            # Return None to let LLM judge decide
            pass
        
        # All other cases need LLM judge
        return None
    
    def _llm_judge(
        self,
        run_summary: str,
        task_text: str,
        outcome: str,
        references: List[Dict[str, Any]],
        artifacts: List[Dict[str, Any]],
        similar_runs: List[SimilarRun]
    ) -> MemoryDecision:
        """
        Stage 2: LLM judge for ambiguous cases.
        
        LLM must choose: ADD, NOT, REPLACE, or MERGE
        """
        # Prepare context for LLM
        similar_runs_context = []
        for run in similar_runs:
            similar_runs_context.append({
                "run_id": run.run_id,
                "summary": run.summary,
                "outcome": run.outcome,
                "similarity": run.similarity,
                "references_count": len(run.references),
                "artifacts_count": len(run.artifacts)
            })
        
        # Build prompt
        prompt = self._build_decision_prompt(
            current_summary=run_summary,
            task_text=task_text,
            outcome=outcome,
            references_count=len(references),
            artifacts_count=len(artifacts),
            similar_runs=similar_runs_context
        )
        
        # Call LLM with structured output
        try:
            decision_json = self.llm_service.make_decision(prompt)
            # Log the raw LLM response for debugging
            print(f"[DEBUG] LLM raw response: {decision_json}")
        except Exception as e:
            # Fallback to ADD on LLM call error
            print(f"[ERROR] LLM call failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return MemoryDecision(
                run_id="",  # Will be set by caller
                decision="ADD",
                reason=f"Error calling LLM: {str(e)}. Defaulting to ADD.",
                similarity_score=similar_runs[0].similarity if similar_runs else None,
                timestamp=datetime.now(timezone.utc)
            )
        
        # Parse and validate decision
        try:
            print(f"[DEBUG] Parsing decision JSON: {decision_json[:200]}...")  # Log first 200 chars
            # Try to extract JSON from response (in case LLM adds extra text)
            if isinstance(decision_json, str):
                # Clean the response - remove markdown code blocks if present
                cleaned = decision_json.strip()
                if cleaned.startswith("```json"):
                    cleaned = cleaned[7:]  # Remove ```json
                elif cleaned.startswith("```"):
                    cleaned = cleaned[3:]  # Remove ```
                if cleaned.endswith("```"):
                    cleaned = cleaned[:-3]  # Remove closing ```
                cleaned = cleaned.strip()
                
                # First try direct JSON parse
                try:
                    decision_data = json.loads(cleaned)
                except json.JSONDecodeError:
                    # If that fails, try to extract JSON object
                    # Match balanced braces
                    brace_count = 0
                    start_idx = cleaned.find('{')
                    if start_idx != -1:
                        for i in range(start_idx, len(cleaned)):
                            if cleaned[i] == '{':
                                brace_count += 1
                            elif cleaned[i] == '}':
                                brace_count -= 1
                                if brace_count == 0:
                                    extracted_json = cleaned[start_idx:i+1]
                                    decision_data = json.loads(extracted_json)
                                    break
                        else:
                            # Fallback: try regex for nested JSON
                            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', cleaned, re.DOTALL)
                            if json_match:
                                decision_data = json.loads(json_match.group(0))
                            else:
                                raise json.JSONDecodeError("Could not extract JSON from response", cleaned, 0)
                    else:
                        raise json.JSONDecodeError("No JSON object found in response", cleaned, 0)
            else:
                decision_data = decision_json
            
            decision = decision_data.get("decision", "ADD").upper()
            target_run_id = decision_data.get("target_run_id")
            reason = decision_data.get("reason", "No reason provided")
            
            # Validate decision
            if decision not in ["ADD", "NOT", "REPLACE", "MERGE"]:
                decision = "ADD"  # Default to ADD if invalid
            
            # Validate target_run_id for REPLACE/MERGE
            if decision in ["REPLACE", "MERGE"]:
                if not target_run_id:
                    # Try to use best match if not specified
                    if similar_runs:
                        target_run_id = similar_runs[0].run_id
                    else:
                        decision = "ADD"  # Fallback to ADD if no target
                        target_run_id = None
            
            return MemoryDecision(
                run_id="",  # Will be set by caller
                decision=decision,
                target_run_id=target_run_id,
                reason=reason,
                similarity_score=similar_runs[0].similarity if similar_runs else None,
                timestamp=datetime.now(timezone.utc)
            )
            
        except Exception as e:
            # Fallback to ADD on error
            print(f"[ERROR] Failed to parse LLM decision: {str(e)}")
            print(f"[ERROR] Raw response was: {decision_json}")
            import traceback
            traceback.print_exc()
            return MemoryDecision(
                run_id="",  # Will be set by caller
                decision="ADD",
                reason=f"Error in LLM decision: {str(e)}. Defaulting to ADD.",
                similarity_score=similar_runs[0].similarity if similar_runs else None,
                timestamp=datetime.now(timezone.utc)
            )
    
    def _build_decision_prompt(
        self,
        current_summary: str,
        task_text: str,
        outcome: str,
        references_count: int,
        artifacts_count: int,
        similar_runs: List[Dict[str, Any]]
    ) -> str:
        """Build the prompt for LLM decision making."""
        similar_runs_text = "\n".join([
            f"- Run ID: {r['run_id']}\n"
            f"  Summary: {r['summary']}\n"
            f"  Outcome: {r['outcome']}\n"
            f"  Similarity: {r['similarity']:.2f}\n"
            f"  References: {r['references_count']}, Artifacts: {r['artifacts_count']}"
            for r in similar_runs
        ])
        
        prompt = f"""You are deciding whether to store a new agent run in long-term memory.

NEW RUN:
Task: {task_text}
Summary: {current_summary}
Outcome: {outcome}
References: {references_count}
Artifacts: {artifacts_count}

SIMILAR EXISTING RUNS:
{similar_runs_text if similar_runs else "None found"}

Choose exactly ONE action:

ADD: The new run adds valuable, non-redundant information
NOT: The new run is redundant or adds little value compared to existing runs
REPLACE: The new run is a better version of an existing run (specify target_run_id)
MERGE: The new run is similar but complementary to an existing run (specify target_run_id)

Prioritize:
- Correctness and usefulness
- Avoiding redundancy
- Preserving valuable patterns
- Replacing outdated information when appropriate

CRITICAL: You MUST respond with ONLY valid JSON. No markdown, no code blocks, no explanations outside the JSON. Start with {{ and end with }}.

Required JSON format:
{{
  "decision": "ADD",
  "target_run_id": null,
  "reason": "brief explanation"
}}

For REPLACE or MERGE, set target_run_id to the run_id from SIMILAR EXISTING RUNS above.
For ADD or NOT, set target_run_id to null."""
        
        return prompt
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        v1 = np.array(vec1)
        v2 = np.array(vec2)
        dot_product = np.dot(v1, v2)
        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return float(dot_product / (norm1 * norm2))
    
    def store_decision(self, decision: MemoryDecision) -> None:
        """Store decision for observability."""
        with self.driver.session() as session:
            session.run("""
                MERGE (d:MemoryDecision {run_id: $run_id})
                SET d.decision = $decision,
                    d.target_run_id = $target_run_id,
                    d.reason = $reason,
                    d.similarity_score = $similarity_score,
                    d.timestamp = $timestamp
            """,
                run_id=decision.run_id,
                decision=decision.decision,
                target_run_id=decision.target_run_id,
                reason=decision.reason,
                similarity_score=decision.similarity_score,
                timestamp=decision.timestamp.isoformat()
            )

