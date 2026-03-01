"""Memory Builder - processes completed runs and stores them in Neo4j.

Pipeline (Task as spine):
1. Summarize run
2. Extract task label (LLM: "In 3-5 words, what was this about?")
3. Normalize task (get_or_create via semantic similarity)
4. Create Run node
5. Link (Run)-[:ABOUT_TASK]->(Task)
"""
import hashlib
import json
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import numpy as np
from neo4j import Driver

from db.connection import get_neo4j_driver
from models.run import RunPayload
from models.decision import MemoryDecision
from services.embedding import EmbeddingService
from services.llm import LLMService
from services.decision import DecisionLayer
import config


class MemoryBuilder:
    """Builds and stores memory from agent runs. Task = branch, Run = leaf."""

    def __init__(self):
        self.driver = get_neo4j_driver()
        self.embedding_service = EmbeddingService()
        self.llm_service = LLMService()
        self.decision_layer = DecisionLayer()
        self.similarity_threshold = config.Config.SIMILARITY_THRESHOLD

    def process_run(self, payload: RunPayload) -> Dict[str, Any]:
        """
        Process a completed run and store it in the knowledge graph.

        Pipeline:
        1. Summarize run
        2. Extract task label (LLM)
        3. Normalize task (get_or_create)
        4. Decision (add / skip / replace)
        5. Create Run and link (Run)-[:ABOUT_TASK]->(Task)
        """
        try:
            run_tree_dict = payload.get_run_tree()
            outcome = payload.get_outcome()

            # Step 1: Summarize run
            summary, reason_added = self.llm_service.summarize_run(run_tree_dict, outcome)
            summary_embedding = self.embedding_service.embed(summary)

            # Step 2: Extract task label (dynamic, not from user_task)
            task_label = self.llm_service.extract_task_label(run_tree_dict)

            # Step 3: Normalize task (get_or_create via semantic similarity)
            task_id = self._get_or_create_task(task_label)

            # Step 4: Decision layer (simplified - no references/artifacts)
            try:
                decision = self.decision_layer.decide(
                    run_id=payload.run_id,
                    run_summary=summary,
                    run_embedding=summary_embedding,
                    task_text=task_label,
                    outcome=outcome,
                    agent_id=payload.agent_id,
                    user_id=payload.user_id,
                )
            except Exception as e:
                import traceback

                error_msg = f"Error in decision layer: {str(e)}\n{traceback.format_exc()}"
                print(f"[ERROR] {error_msg}")
                raise Exception(error_msg) from e

            if decision.decision == "NOT":
                self.decision_layer.store_decision(decision)
                result = {
                    "success": True,
                    "decision": "NOT",
                    "reason": decision.reason,
                    "message": "Run not added to memory (redundant or low value)",
                    "similarity_score": decision.similarity_score,
                }
                if decision.similar_runs:
                    result["similar_runs"] = decision.similar_runs
                return result

            # Handle REPLACE: mark old run as superseded
            if decision.decision == "REPLACE" and decision.target_run_id:
                self._mark_run_superseded(decision.target_run_id, payload.run_id)

            # Step 5: Create Run and link (Run)-[:ABOUT_TASK]->(Task)
            if not (reason_added or "").strip():
                reason_added = "• Run added to memory for future retrieval."
            run_id = self._create_run(
                payload=payload,
                summary=summary,
                summary_embedding=summary_embedding,
                task_id=task_id,
                run_tree_dict=run_tree_dict,
                status="active",
                reason_added=reason_added,
            )

            self.decision_layer.store_decision(decision)
            result = {
                "success": True,
                "decision": decision.decision,
                "run_id": run_id,
                "task_id": task_id,
                "task_label": task_label,
                "target_run_id": decision.target_run_id,
                "reason": decision.reason,
                "summary": summary,
                "reason_added": reason_added,
            }
            return result

        except Exception as e:
            import traceback

            error_str = str(e)
            error_traceback = traceback.format_exc()
            print(f"[ERROR] Exception in process_run:\n{error_traceback}")
            return {
                "success": False,
                "error": f"{error_str}\n\nTraceback:\n{error_traceback}",
            }

    def _get_or_create_task(self, label: str) -> str:
        """
        get_or_create_task: normalize task via semantic similarity.
        If similar Task exists above THRESHOLD, reuse. Else create new.
        """
        task_embedding = self.embedding_service.embed(label)
        task_id = self._generate_id("task", label)

        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (t:Task)
                WHERE t.embedding IS NOT NULL
                RETURN t.id AS id, t.embedding AS embedding
            """
            )
            expected_dim = len(task_embedding)
            best_match = None
            best_similarity = 0.0

            for record in result:
                task_emb = record["embedding"]
                if len(task_emb) != expected_dim:
                    continue
                try:
                    similarity = self._cosine_similarity(task_embedding, task_emb)
                    if similarity >= self.similarity_threshold and similarity > best_similarity:
                        best_similarity = similarity
                        best_match = record["id"]
                except Exception:
                    continue

            if best_match:
                return best_match

            # Create new Task
            session.run(
                """
                MERGE (t:Task {id: $id})
                SET t.label = $label,
                    t.embedding = $embedding
            """,
                id=task_id,
                label=label,
                embedding=task_embedding,
            )
            return task_id

    def _create_run(
        self,
        payload: RunPayload,
        summary: str,
        summary_embedding: List[float],
        task_id: str,
        run_tree_dict: Dict[str, Any],
        status: str = "active",
        reason_added: Optional[str] = None,
    ) -> str:
        """Create Run node and link (Run)-[:ABOUT_TASK]->(Task)."""
        run_id = payload.run_id
        created_at = payload.get_created_at() or datetime.now(timezone.utc)
        outcome = payload.get_outcome()

        with self.driver.session() as session:
            run_tree_json = json.dumps(run_tree_dict)

            # Create Run node (outcome as property, not separate node)
            session.run(
                """
                MERGE (r:Run {id: $run_id})
                SET r.agent_id = $agent_id,
                    r.user_id = $user_id,
                    r.summary = $summary,
                    r.embedding = $embedding,
                    r.run_tree = $run_tree,
                    r.created_at = $created_at,
                    r.status = $status,
                    r.reason_added = $reason_added,
                    r.outcome = $outcome
            """,
                run_id=run_id,
                agent_id=payload.agent_id,
                user_id=payload.user_id or "",
                summary=summary,
                embedding=summary_embedding,
                run_tree=run_tree_json,
                created_at=created_at.isoformat(),
                status=status,
                reason_added=reason_added or "",
                outcome=outcome,
            )

            # Link (Run)-[:ABOUT_TASK]->(Task) - runs point to tasks
            session.run(
                """
                MATCH (t:Task {id: $task_id})
                MATCH (r:Run {id: $run_id})
                MERGE (r)-[:ABOUT_TASK]->(t)
            """,
                task_id=task_id,
                run_id=run_id,
            )

        return run_id

    def _generate_id(self, prefix: str, content: str) -> str:
        """Generate a deterministic ID from content."""
        hash_obj = hashlib.sha256(content.encode())
        hash_hex = hash_obj.hexdigest()[:16]
        return f"{prefix}_{hash_hex}"

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

    def _mark_run_superseded(self, old_run_id: str, new_run_id: str) -> None:
        """Mark an old run as superseded by a new run."""
        with self.driver.session() as session:
            session.run(
                """
                MATCH (r:Run {id: $old_run_id})
                SET r.status = 'superseded',
                    r.superseded_by = $new_run_id
            """,
                old_run_id=old_run_id,
                new_run_id=new_run_id,
            )
