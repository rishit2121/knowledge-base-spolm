"""Memory Retrieval API - retrieves relevant information from the knowledge graph.

Retrieval pipeline (Task as spine):
1. Semantic search over Runs → find most similar Run to new task
2. Jump to its Task (Run)-[:ABOUT_TASK]->(Task)
3. Get sibling Runs (all runs on same Task)
4. Summarize patterns: "Previous runs for this task usually succeeded when X, failed when Y"
"""
from typing import List, Dict, Any, Optional
import json
import numpy as np
from neo4j import Driver

from db.connection import get_neo4j_driver
from models.retrieval import RetrievalRequest, RetrievalResponse, RelatedRun
from services.embedding import EmbeddingService
import config


class MemoryRetrieval:
    """Retrieves relevant memory from the knowledge graph."""

    def __init__(self):
        self.driver = get_neo4j_driver()
        self.embedding_service = EmbeddingService()

    def retrieve(self, request: RetrievalRequest) -> RetrievalResponse:
        """
        Retrieve relevant memory for a given task.

        Pipeline:
        1. Semantic search over Runs (find most similar)
        2. Jump to Task via ABOUT_TASK
        3. Get sibling Runs (same Task)
        4. Summarize patterns across siblings
        """
        query_text = request.context or request.task_text
        query_embedding = self.embedding_service.embed(query_text)

        # Step 1: Vector search for similar Runs
        similar_runs = self._vector_search_runs(
            query_embedding,
            top_k=request.top_k,
            user_id=request.user_id,
            agent_id=request.agent_id,
        )

        if not similar_runs:
            return RetrievalResponse(
                observations=["No similar runs found in memory."],
                related_runs=[],
                confidence=0.0,
                query_embedding=query_embedding,
            )

        # Step 2 & 3: For each similar run, jump to its Task and get sibling Runs
        related_runs = []
        seen_run_ids = set()
        for run_data in similar_runs:
            expanded = self._expand_run_via_task(
                run_data["run_id"],
                run_data["similarity"],
                user_id=request.user_id,
                agent_id=request.agent_id,
            )
            for run in expanded:
                if run.run_id not in seen_run_ids:
                    seen_run_ids.add(run.run_id)
                    related_runs.append(run)

        # Deduplicate and limit
        related_runs = related_runs[: request.top_k * 2]  # Allow more from siblings

        # Step 4: Analyze patterns across runs (especially siblings on same task)
        observations = self._analyze_patterns(related_runs)
        confidence = self._calculate_confidence(related_runs)

        return RetrievalResponse(
            observations=observations,
            related_runs=related_runs,
            confidence=confidence,
            query_embedding=query_embedding,
        )

    def _vector_search_runs(
        self,
        query_embedding: List[float],
        top_k: int,
        user_id: str = None,
        agent_id: str = None,
    ) -> List[Dict[str, Any]]:
        """Search for similar runs using vector similarity."""
        with self.driver.session() as session:
            where_clauses = [
                "r.embedding IS NOT NULL",
                "(r.status IS NULL OR r.status = 'active')",
            ]
            params = {}
            if user_id:
                where_clauses.append("r.user_id = $user_id")
                params["user_id"] = user_id
            if agent_id:
                where_clauses.append("r.agent_id = $agent_id")
                params["agent_id"] = agent_id

            result = session.run(
                f"""
                MATCH (r:Run)
                WHERE {' AND '.join(where_clauses)}
                RETURN r.id AS run_id, r.embedding AS embedding
            """,
                **params,
            )

            expected_dim = len(query_embedding)
            runs_with_similarity = []
            for record in result:
                run_embedding = record["embedding"]
                if len(run_embedding) != expected_dim:
                    continue
                try:
                    similarity = self._cosine_similarity(query_embedding, run_embedding)
                    runs_with_similarity.append(
                        {"run_id": record["run_id"], "similarity": similarity}
                    )
                except Exception:
                    continue

            runs_with_similarity.sort(key=lambda x: x["similarity"], reverse=True)
            return runs_with_similarity[:top_k]

    def _expand_run_via_task(
        self,
        run_id: str,
        similarity: float,
        user_id: str = None,
        agent_id: str = None,
    ) -> List[RelatedRun]:
        """
        Expand a run: get Run details and all sibling Runs (same Task).
        Returns list of RelatedRun including the seed and siblings.
        """
        with self.driver.session() as session:
            params = {"run_id": run_id}
            sibling_where = ["(sibling.status IS NULL OR sibling.status = 'active')"]
            if user_id:
                sibling_where.append("sibling.user_id = $user_id")
                params["user_id"] = user_id
            if agent_id:
                sibling_where.append("sibling.agent_id = $agent_id")
                params["agent_id"] = agent_id

            result = session.run(
                f"""
                MATCH (r:Run {{id: $run_id}})-[:ABOUT_TASK]->(t:Task)
                MATCH (sibling:Run)-[:ABOUT_TASK]->(t)
                WHERE {' AND '.join(sibling_where)}
                RETURN r.id AS seed_run_id,
                       r.summary AS summary,
                       r.reason_added AS reason_added,
                       r.outcome AS outcome,
                       r.run_tree AS run_tree,
                       r.agent_id AS agent_id,
                       r.user_id AS user_id,
                       t.label AS task_label,
                       collect(DISTINCT {{
                           id: sibling.id,
                           summary: sibling.summary,
                           reason_added: sibling.reason_added,
                           outcome: sibling.outcome,
                           run_tree: sibling.run_tree,
                           agent_id: sibling.agent_id,
                           user_id: sibling.user_id
                       }}) AS siblings
            """,
                **params,
            )

            record = result.single()
            if not record:
                # Fallback: just get the run without task/siblings
                return self._expand_run_simple(run_id, similarity)

            run_tree = None
            if record["run_tree"]:
                try:
                    run_tree = json.loads(record["run_tree"])
                except (json.JSONDecodeError, TypeError):
                    run_tree = None

            related = []
            # Add seed run
            related.append(
                RelatedRun(
                    run_id=record["seed_run_id"],
                    user_id=record["user_id"],
                    agent_id=record["agent_id"],
                    summary=record["summary"],
                    reason_added=record.get("reason_added") or "",
                    outcome=record["outcome"] or "unknown",
                    run_tree=run_tree,
                    references=[],
                    artifacts=[],
                    similarity_score=similarity,
                )
            )

            # Add siblings (use same similarity for seed's task context)
            for s in (record["siblings"] or []):
                if not s or not s.get("id"):
                    continue
                if s["id"] == record["seed_run_id"]:
                    continue
                s_run_tree = None
                if s.get("run_tree"):
                    try:
                        s_run_tree = json.loads(s["run_tree"])
                    except (json.JSONDecodeError, TypeError):
                        pass
                related.append(
                    RelatedRun(
                        run_id=s["id"],
                        user_id=s.get("user_id"),
                        agent_id=s.get("agent_id", ""),
                        summary=s.get("summary", ""),
                        reason_added=s.get("reason_added") or "",
                        outcome=s.get("outcome") or "unknown",
                        run_tree=s_run_tree,
                        references=[],
                        artifacts=[],
                        similarity_score=similarity * 0.9,  # Slightly lower for siblings
                    )
                )

            return related

    def _expand_run_simple(self, run_id: str, similarity: float) -> List[RelatedRun]:
        """Fallback: get run without task/siblings."""
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (r:Run {id: $run_id})
                RETURN r.id AS run_id,
                       r.agent_id AS agent_id,
                       r.user_id AS user_id,
                       r.summary AS summary,
                       r.reason_added AS reason_added,
                       r.run_tree AS run_tree,
                       r.outcome AS outcome
            """,
                run_id=run_id,
            )
            record = result.single()
            if not record:
                return []

            run_tree = None
            if record["run_tree"]:
                try:
                    run_tree = json.loads(record["run_tree"])
                except (json.JSONDecodeError, TypeError):
                    pass

            return [
                RelatedRun(
                    run_id=record["run_id"],
                    user_id=record["user_id"],
                    agent_id=record["agent_id"],
                    summary=record["summary"],
                    reason_added=record.get("reason_added") or "",
                    outcome=record["outcome"] or "unknown",
                    run_tree=run_tree,
                    references=[],
                    artifacts=[],
                    similarity_score=similarity,
                )
            ]

    def _analyze_patterns(self, related_runs: List[RelatedRun]) -> List[str]:
        """
        Analyze patterns: "Previous runs for this task usually succeeded when X,
        failed when Y."
        """
        if not related_runs:
            return ["No similar runs found in memory."]

        observations = []
        outcomes = [r.outcome for r in related_runs]
        success_count = outcomes.count("success")
        failure_count = outcomes.count("failure")
        partial_count = outcomes.count("partial")

        if success_count > 0:
            observations.append(
                f"Found {success_count} successful similar run(s). Review their approaches for reference."
            )
        if failure_count > 0:
            observations.append(
                f"Found {failure_count} failed similar run(s). Be aware of potential pitfalls."
            )
        if partial_count > 0 and (success_count + failure_count) > 0:
            observations.append(
                f"{partial_count} partial run(s) in this task group."
            )

        high_similarity = [r for r in related_runs if r.similarity_score > 0.9]
        if high_similarity:
            observations.append(
                f"{len(high_similarity)} run(s) with very high similarity (>0.9). "
                "Consider reusing their approaches."
            )

        return observations

    def _calculate_confidence(self, related_runs: List[RelatedRun]) -> float:
        """Calculate confidence from count, similarity, outcome consistency."""
        if not related_runs:
            return 0.0

        count_confidence = min(len(related_runs) / 5.0, 1.0)
        avg_similarity = sum(r.similarity_score for r in related_runs) / len(related_runs)
        outcomes = [r.outcome for r in related_runs]
        outcome_confidence = 1.0 if len(set(outcomes)) == 1 else 0.7

        confidence = (
            0.3 * count_confidence + 0.5 * avg_similarity + 0.2 * outcome_confidence
        )
        return round(confidence, 2)

    def retrieve_all(
        self,
        user_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Retrieve all runs from the knowledge graph."""
        with self.driver.session() as session:
            where_clauses = ["(r.status IS NULL OR r.status = 'active')"]
            params = {}
            if user_id:
                where_clauses.append("r.user_id = $user_id")
                params["user_id"] = user_id
            if agent_id:
                where_clauses.append("r.agent_id = $agent_id")
                params["agent_id"] = agent_id

            limit_clause = f"LIMIT {limit}" if limit else ""

            result = session.run(
                f"""
                MATCH (r:Run)
                WHERE {' AND '.join(where_clauses)}
                OPTIONAL MATCH (r)-[:ABOUT_TASK]->(t:Task)
                RETURN r.id AS run_id,
                       r.agent_id AS agent_id,
                       r.user_id AS user_id,
                       r.summary AS summary,
                       r.reason_added AS reason_added,
                       r.run_tree AS run_tree,
                       r.outcome AS outcome,
                       r.created_at AS created_at,
                       t.label AS task_label
                ORDER BY r.created_at DESC
                {limit_clause}
            """,
                **params,
            )

            runs = []
            for record in result:
                run_tree = None
                if record["run_tree"]:
                    try:
                        run_tree = json.loads(record["run_tree"])
                    except (json.JSONDecodeError, TypeError):
                        pass

                created_at = None
                if record["created_at"]:
                    created_at = (
                        str(record["created_at"])
                        if not isinstance(record["created_at"], str)
                        else record["created_at"]
                    )

                runs.append(
                    {
                        "run_id": record["run_id"],
                        "user_id": record["user_id"],
                        "agent_id": record["agent_id"],
                        "summary": record["summary"],
                        "reason_added": record.get("reason_added") or "",
                        "outcome": record["outcome"] or "unknown",
                        "run_tree": run_tree,
                        "references": [],
                        "artifacts": [],
                        "created_at": created_at,
                        "task_label": record.get("task_label"),
                    }
                )

            return runs

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        v1 = np.array(vec1)
        v2 = np.array(vec2)
        dot_product = np.dot(v1, v2)
        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return float(dot_product / (norm1 * norm2))
