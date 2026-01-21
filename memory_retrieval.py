"""Memory Retrieval API - retrieves relevant information from the knowledge graph."""
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
        1. Embed input
        2. Vector search for similar Tasks/Runs
        3. Expand locally (get references, artifacts, outcomes)
        4. Analyze patterns
        5. Summarize for agent
        
        Args:
            request: Retrieval request
            
        Returns:
            Retrieval response with observations and related runs
        """
        # Step 1: Embed input
        query_text = request.context or request.task_text
        query_embedding = self.embedding_service.embed(query_text)
        
        # Step 2: Vector search for similar Runs
        similar_runs = self._vector_search_runs(
            query_embedding,
            top_k=request.top_k,
            agent_id=request.agent_id
        )
        
        # Step 3: Expand locally - get full context for each run
        related_runs = []
        for run_data in similar_runs:
            expanded = self._expand_run(run_data["run_id"])
            if expanded:
                related_runs.append(RelatedRun(
                    run_id=expanded["run_id"],
                    agent_id=expanded["agent_id"],
                    summary=expanded["summary"],
                    outcome=expanded["outcome"],
                    run_tree=expanded.get("run_tree"),
                    references=expanded["references"],
                    artifacts=expanded["artifacts"],
                    similarity_score=run_data["similarity"]
                ))
        
        # Step 4: Analyze patterns and generate observations
        observations = self._analyze_patterns(related_runs)
        
        # Step 5: Calculate confidence
        confidence = self._calculate_confidence(related_runs)
        
        return RetrievalResponse(
            observations=observations,
            related_runs=related_runs,
            confidence=confidence,
            query_embedding=query_embedding
        )
    
    def _vector_search_runs(
        self,
        query_embedding: List[float],
        top_k: int,
        agent_id: str = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar runs using vector similarity.
        
        Returns list of dicts with run_id and similarity score.
        """
        with self.driver.session() as session:
            # Build query with optional agent filter
            agent_filter = "AND r.agent_id = $agent_id" if agent_id else ""
            
            # Manual cosine similarity calculation
            # For Neo4j 5.11+ with vector indexes, use: db.index.vector.queryNodes
            
            query = f"""
                MATCH (r:Run)
                WHERE r.embedding IS NOT NULL
                  AND (r.status IS NULL OR r.status = 'active')
                  {agent_filter}
                RETURN r.id AS run_id, r.embedding AS embedding
            """
            
            params = {}
            if agent_id:
                params["agent_id"] = agent_id
            
            result = session.run(query, **params)
            
            # Calculate similarity in Python
            # Only compare with embeddings that have the same dimension
            expected_dim = len(query_embedding)
            runs_with_similarity = []
            for record in result:
                run_embedding = record["embedding"]
                # Skip embeddings with wrong dimension (from different model)
                if len(run_embedding) != expected_dim:
                    continue
                try:
                    similarity = self._cosine_similarity(query_embedding, run_embedding)
                    runs_with_similarity.append({
                        "run_id": record["run_id"],
                        "similarity": similarity
                    })
                except Exception as e:
                    # Skip if similarity calculation fails (dimension mismatch, etc.)
                    continue
            
            # Sort by similarity and return top_k
            runs_with_similarity.sort(key=lambda x: x["similarity"], reverse=True)
            return runs_with_similarity[:top_k]
    
    def _expand_run(self, run_id: str) -> Dict[str, Any]:
        """
        Expand a run to get all related nodes (references, artifacts, outcome).
        
        Returns full run context.
        """
        with self.driver.session() as session:
            result = session.run("""
                MATCH (r:Run {id: $run_id})
                OPTIONAL MATCH (r)-[:READS]->(ref:Reference)
                OPTIONAL MATCH (r)-[:WRITES]->(a:Artifact)
                OPTIONAL MATCH (r)-[:ENDED_WITH]->(o:Outcome)
                RETURN r.id AS run_id,
                       r.agent_id AS agent_id,
                       r.summary AS summary,
                       r.run_tree AS run_tree,
                       collect(DISTINCT {
                           id: ref.id,
                           type: ref.type,
                           source_ref: ref.source_ref
                       }) AS references,
                       collect(DISTINCT {
                           id: a.id,
                           type: a.type,
                           hash: a.hash
                       }) AS artifacts,
                       o.label AS outcome
            """, run_id=run_id)
            
            record = result.single()
            if not record:
                return None
            
            # Filter out None values from collections
            references = [r for r in (record["references"] or []) if r.get("id")]
            artifacts = [a for a in (record["artifacts"] or []) if a.get("id")]
            
            # Parse run_tree JSON back to dict
            run_tree = None
            if record["run_tree"]:
                try:
                    run_tree = json.loads(record["run_tree"])
                except (json.JSONDecodeError, TypeError):
                    run_tree = None
            
            return {
                "run_id": record["run_id"],
                "agent_id": record["agent_id"],
                "summary": record["summary"],
                "outcome": record["outcome"] or "unknown",
                "run_tree": run_tree,
                "references": references,
                "artifacts": artifacts
            }
    
    def _analyze_patterns(self, related_runs: List[RelatedRun]) -> List[str]:
        """
        Analyze patterns in related runs and generate observations.
        
        Compares:
        - success vs failure
        - references present vs missing
        - artifact types produced
        """
        if not related_runs:
            return ["No similar runs found in memory."]
        
        observations = []
        
        # Success vs failure analysis
        outcomes = [run.outcome for run in related_runs]
        success_count = outcomes.count("success")
        failure_count = outcomes.count("failure")
        partial_count = outcomes.count("partial")
        
        if success_count > 0:
            observations.append(
                f"Found {success_count} successful similar run(s). "
                f"Review their approaches for reference."
            )
        if failure_count > 0:
            observations.append(
                f"Found {failure_count} failed similar run(s). "
                f"Be aware of potential pitfalls."
            )
        
        # Reference analysis
        all_ref_types = set()
        for run in related_runs:
            for ref in run.references:
                all_ref_types.add(ref.get("type", "unknown"))
        
        if all_ref_types:
            observations.append(
                f"Similar runs typically reference: {', '.join(sorted(all_ref_types))}"
            )
        
        # Artifact analysis
        all_artifact_types = set()
        for run in related_runs:
            for art in run.artifacts:
                all_artifact_types.add(art.get("type", "unknown"))
        
        if all_artifact_types:
            observations.append(
                f"Similar runs typically produce: {', '.join(sorted(all_artifact_types))}"
            )
        
        # High similarity note
        high_similarity_runs = [r for r in related_runs if r.similarity_score > 0.9]
        if high_similarity_runs:
            observations.append(
                f"{len(high_similarity_runs)} run(s) with very high similarity (>0.9). "
                f"Consider reusing their approaches."
            )
        
        return observations
    
    def _calculate_confidence(self, related_runs: List[RelatedRun]) -> float:
        """
        Calculate confidence score based on:
        - Number of similar runs
        - Average similarity score
        - Outcome distribution
        """
        if not related_runs:
            return 0.0
        
        # Base confidence from number of results
        count_confidence = min(len(related_runs) / 5.0, 1.0)
        
        # Similarity confidence
        avg_similarity = sum(r.similarity_score for r in related_runs) / len(related_runs)
        similarity_confidence = avg_similarity
        
        # Outcome consistency (higher if outcomes are consistent)
        outcomes = [r.outcome for r in related_runs]
        if len(set(outcomes)) == 1:
            outcome_confidence = 1.0
        else:
            outcome_confidence = 0.7
        
        # Weighted combination
        confidence = (
            0.3 * count_confidence +
            0.5 * similarity_confidence +
            0.2 * outcome_confidence
        )
        
        return round(confidence, 2)
    
    def retrieve_all(self, agent_id: Optional[str] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Retrieve all runs from the knowledge graph.
        
        Args:
            agent_id: Optional filter by agent ID
            limit: Optional limit on number of runs to return
            
        Returns:
            List of run details with full context
        """
        with self.driver.session() as session:
            # Build WHERE clause with optional filters
            where_conditions = ["(r.status IS NULL OR r.status = 'active')"]
            if agent_id:
                where_conditions.append("r.agent_id = $agent_id")
            
            where_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""
            limit_clause = f"LIMIT {limit}" if limit else ""
            
            query = f"""
                MATCH (r:Run)
                {where_clause}
                OPTIONAL MATCH (r)-[:READS]->(ref:Reference)
                OPTIONAL MATCH (r)-[:WRITES]->(a:Artifact)
                OPTIONAL MATCH (r)-[:ENDED_WITH]->(o:Outcome)
                RETURN r.id AS run_id,
                       r.agent_id AS agent_id,
                       r.summary AS summary,
                       r.run_tree AS run_tree,
                       r.created_at AS created_at,
                       collect(DISTINCT {{
                           id: ref.id,
                           type: ref.type,
                           source_ref: ref.source_ref
                       }}) AS references,
                       collect(DISTINCT {{
                           id: a.id,
                           type: a.type,
                           hash: a.hash
                       }}) AS artifacts,
                       o.label AS outcome
                ORDER BY r.created_at DESC
                {limit_clause}
            """
            
            params = {}
            if agent_id:
                params["agent_id"] = agent_id
            
            result = session.run(query, **params)
            
            runs = []
            for record in result:
                # Filter out None values from collections
                references = [r for r in (record["references"] or []) if r.get("id")]
                artifacts = [a for a in (record["artifacts"] or []) if a.get("id")]
                
                # Parse run_tree JSON back to dict
                run_tree = None
                if record["run_tree"]:
                    try:
                        run_tree = json.loads(record["run_tree"])
                    except (json.JSONDecodeError, TypeError):
                        run_tree = None
                
                # Format created_at if it exists
                created_at = None
                if record["created_at"]:
                    if isinstance(record["created_at"], str):
                        created_at = record["created_at"]
                    else:
                        # If it's a datetime object, convert to ISO string
                        created_at = str(record["created_at"])
                
                runs.append({
                    "run_id": record["run_id"],
                    "agent_id": record["agent_id"],
                    "summary": record["summary"],
                    "outcome": record["outcome"] or "unknown",
                    "run_tree": run_tree,
                    "references": references,
                    "artifacts": artifacts,
                    "created_at": created_at
                })
            
            return runs
    
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

