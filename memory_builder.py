"""Memory Builder - processes completed runs and stores them in Neo4j."""
import hashlib
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
import numpy as np
from neo4j import Driver

from db.connection import get_neo4j_driver
from models.run import RunPayload, Reference, Artifact
from services.embedding import EmbeddingService
from services.llm import LLMService
import config


class MemoryBuilder:
    """Builds and stores memory from agent runs."""
    
    def __init__(self):
        self.driver = get_neo4j_driver()
        self.embedding_service = EmbeddingService()
        self.llm_service = LLMService()
        self.similarity_threshold = config.Config.SIMILARITY_THRESHOLD
    
    def process_run(self, payload: RunPayload) -> Dict[str, Any]:
        """
        Process a completed run and store it in the knowledge graph.
        
        This implements the full Memory Builder pipeline:
        1. Task upsert
        2. Summarize run
        3. Extract references
        4. Extract artifacts
        5. Attach outcome
        
        Args:
            payload: The run payload to process
            
        Returns:
            Dictionary with processing results
        """
        try:
            # Step 1: Task upsert
            task_text = payload.get_task_text()
            if not task_text:
                raise ValueError("task_text or user_task must be provided")
            task_id = self._upsert_task(task_text)
            
            # Step 2: Summarize run
            run_tree_dict = payload.get_run_tree()
            outcome = payload.get_outcome()
            summary = self.llm_service.summarize_run(run_tree_dict, outcome)
            summary_embedding = self.embedding_service.embed(summary)
            
            # Step 3: Extract and store references
            references = self._extract_references(run_tree_dict)
            reference_ids = []
            for ref in references:
                ref_id = self._upsert_reference(ref)
                reference_ids.append(ref_id)
            
            # Step 4: Extract and store artifacts
            artifacts = self._extract_artifacts(run_tree_dict)
            artifact_ids = []
            for artifact in artifacts:
                art_id = self._upsert_artifact(artifact)
                artifact_ids.append(art_id)
            
            # Step 5: Create Run node and relationships
            run_id = self._create_run(
                payload=payload,
                summary=summary,
                summary_embedding=summary_embedding,
                task_id=task_id,
                reference_ids=reference_ids,
                artifact_ids=artifact_ids,
                run_tree_dict=run_tree_dict
            )
            
            return {
                "success": True,
                "run_id": run_id,
                "task_id": task_id,
                "references_count": len(reference_ids),
                "artifacts_count": len(artifact_ids)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _upsert_task(self, task_text: str) -> str:
        """
        Upsert a Task node.
        Finds similar tasks or creates a new one.
        
        Returns:
            Task ID
        """
        task_embedding = self.embedding_service.embed(task_text)
        task_id = self._generate_id("task", task_text)
        
        with self.driver.session() as session:
            # Try to find similar task using vector similarity
            # Note: For Neo4j 5.11+ with vector indexes, you can use db.index.vector.queryNodes
            # This uses manual cosine similarity calculation
            
            # Get all tasks and calculate similarity in Python
            result = session.run("""
                MATCH (t:Task)
                WHERE t.embedding IS NOT NULL
                RETURN t.id AS id, t.embedding AS embedding
            """)
            
            best_match = None
            best_similarity = 0.0
            
            for record in result:
                task_emb = record["embedding"]
                similarity = self._cosine_similarity(task_embedding, task_emb)
                if similarity >= self.similarity_threshold and similarity > best_similarity:
                    best_similarity = similarity
                    best_match = record["id"]
            
            if best_match:
                return best_match
            
            record = result.single()
            
            if record:
                # Reuse existing task
                return record["id"]
            else:
                # Create new task
                session.run("""
                    MERGE (t:Task {id: $id})
                    SET t.text = $text,
                        t.embedding = $embedding
                """, id=task_id, text=task_text, embedding=task_embedding)
                return task_id
    
    def _create_run(
        self,
        payload: RunPayload,
        summary: str,
        summary_embedding: List[float],
        task_id: str,
        reference_ids: List[str],
        artifact_ids: List[str],
        run_tree_dict: Dict[str, Any]
    ) -> str:
        """Create Run node and all relationships."""
        run_id = payload.run_id
        created_at = payload.get_created_at() or datetime.utcnow()
        
        with self.driver.session() as session:
            # Store run_tree as JSON string for later retrieval
            run_tree_json = json.dumps(run_tree_dict)
            
            # Create Run node
            session.run("""
                MERGE (r:Run {id: $run_id})
                SET r.agent_id = $agent_id,
                    r.summary = $summary,
                    r.embedding = $embedding,
                    r.run_tree = $run_tree,
                    r.created_at = $created_at
            """, 
                run_id=run_id,
                agent_id=payload.agent_id,
                summary=summary,
                embedding=summary_embedding,
                run_tree=run_tree_json,
                created_at=created_at.isoformat()
            )
            
            # Link to Task
            session.run("""
                MATCH (t:Task {id: $task_id})
                MATCH (r:Run {id: $run_id})
                MERGE (t)-[:TRIGGERED]->(r)
            """, task_id=task_id, run_id=run_id)
            
            # Link to References
            for ref_id in reference_ids:
                session.run("""
                    MATCH (r:Run {id: $run_id})
                    MATCH (ref:Reference {id: $ref_id})
                    MERGE (r)-[:READS]->(ref)
                """, run_id=run_id, ref_id=ref_id)
            
            # Link to Artifacts
            for art_id in artifact_ids:
                session.run("""
                    MATCH (r:Run {id: $run_id})
                    MATCH (a:Artifact {id: $art_id})
                    MERGE (r)-[:WRITES]->(a)
                """, run_id=run_id, art_id=art_id)
            
            # Create and link Outcome
            outcome = payload.get_outcome()
            session.run("""
                MATCH (r:Run {id: $run_id})
                MERGE (o:Outcome {label: $outcome})
                MERGE (r)-[:ENDED_WITH]->(o)
            """, run_id=run_id, outcome=outcome)
        
        return run_id
    
    def _extract_references(self, run_tree: Dict[str, Any]) -> List[Reference]:
        """
        Extract references from run_tree.
        Looks for: schemas, documents, API responses, prior runs in steps.
        """
        references = []
        
        # Extract from steps array (new structure)
        if "steps" in run_tree and isinstance(run_tree["steps"], list):
            for step in run_tree["steps"]:
                # Check step_input for references
                if "step_input" in step and isinstance(step["step_input"], dict):
                    step_input = step["step_input"]
                    # Look for context, emailData, or other reference-like data
                    if "context" in step_input:
                        context = step_input["context"]
                        if isinstance(context, dict):
                            # Extract email data, API responses, etc.
                            if "emailData" in context:
                                ref_content = json.dumps(context["emailData"], sort_keys=True)
                                ref_id = self._generate_id("ref", ref_content)
                                ref_embedding = self.embedding_service.embed(ref_content)
                                references.append(Reference(
                                    id=ref_id,
                                    type="api_response",  # Email data from API
                                    embedding=ref_embedding,
                                    source_ref=f"step_{step.get('step_id', 'unknown')}.emailData"
                                ))
                
                # Check step_output for references
                if "step_output" in step and isinstance(step["step_output"], dict):
                    step_output = step["step_output"]
                    if "data" in step_output and isinstance(step_output["data"], dict):
                        # Extract structured data from outputs
                        data = step_output["data"]
                        if "id" in data or "messageId" in data:  # Email-like data
                            ref_content = json.dumps(data, sort_keys=True)
                            ref_id = self._generate_id("ref", ref_content)
                            ref_embedding = self.embedding_service.embed(ref_content)
                            references.append(Reference(
                                id=ref_id,
                                type="api_response",
                                embedding=ref_embedding,
                                source_ref=f"step_{step.get('step_id', 'unknown')}.output_data"
                            ))
        
        # Fallback: traverse entire structure (for backward compatibility)
        def traverse(node: Any, path: str = ""):
            if isinstance(node, dict):
                # Check for reference-like structures
                if "type" in node and node.get("type") in ["schema", "document", "api_response", "prior_run"]:
                    ref_type = node.get("type", "unknown")
                    ref_content = json.dumps(node, sort_keys=True)
                    ref_id = self._generate_id("ref", ref_content)
                    ref_embedding = self.embedding_service.embed(ref_content)
                    
                    references.append(Reference(
                        id=ref_id,
                        type=ref_type,
                        embedding=ref_embedding,
                        source_ref=node.get("source", path)
                    ))
                
                # Recursively traverse (but skip steps as we already processed it)
                for key, value in node.items():
                    if key != "steps":  # Skip steps to avoid duplicate processing
                        traverse(value, f"{path}.{key}" if path else key)
            
            elif isinstance(node, list):
                for i, item in enumerate(node):
                    traverse(item, f"{path}[{i}]")
        
        # Only traverse if we didn't find references in steps
        if not references:
            traverse(run_tree)
        
        return references
    
    def _extract_artifacts(self, run_tree: Dict[str, Any]) -> List[Artifact]:
        """
        Extract artifacts from run_tree.
        Looks for: schemas, plans, reports, code outputs in steps.
        """
        artifacts = []
        
        # Extract from steps array (new structure)
        if "steps" in run_tree and isinstance(run_tree["steps"], list):
            for step in run_tree["steps"]:
                step_name = step.get("step_name", "")
                step_type = step.get("step_type", "")
                step_output = step.get("step_output", {})
                
                # Extract artifacts based on step type and output
                if step_type == "llm_call" and isinstance(step_output, dict):
                    # LLM outputs like summaries, replies, reasoning
                    if "data" in step_output:
                        art_content = json.dumps(step_output["data"], sort_keys=True)
                        art_hash = hashlib.sha256(art_content.encode()).hexdigest()
                        art_id = self._generate_id("artifact", art_content)
                        art_embedding = self.embedding_service.embed(art_content)
                        
                        # Determine artifact type from step name
                        if "summary" in step_name.lower():
                            art_type = "report"
                        elif "reply" in step_name.lower() or "generate" in step_name.lower():
                            art_type = "code"  # Generated content
                        elif "reasoning" in step_name.lower():
                            art_type = "plan"
                        else:
                            art_type = "report"
                        
                        artifacts.append(Artifact(
                            id=art_id,
                            type=art_type,
                            embedding=art_embedding,
                            hash=art_hash
                        ))
                
                # Extract from step_input if it contains generated content
                if "step_input" in step and isinstance(step["step_input"], dict):
                    step_input = step["step_input"]
                    if "reply" in step_input or "summary" in step_input:
                        # This is input that was generated in a previous step
                        art_content = json.dumps(step_input, sort_keys=True)
                        art_hash = hashlib.sha256(art_content.encode()).hexdigest()
                        art_id = self._generate_id("artifact", art_content)
                        art_embedding = self.embedding_service.embed(art_content)
                        
                        artifacts.append(Artifact(
                            id=art_id,
                            type="report",
                            embedding=art_embedding,
                            hash=art_hash
                        ))
        
        # Fallback: traverse entire structure (for backward compatibility)
        def traverse(node: Any, path: str = ""):
            if isinstance(node, dict):
                # Check for artifact-like structures
                if "type" in node and node.get("type") in ["schema", "plan", "report", "code"]:
                    art_type = node.get("type", "unknown")
                    art_content = json.dumps(node, sort_keys=True)
                    art_hash = hashlib.sha256(art_content.encode()).hexdigest()
                    art_id = self._generate_id("artifact", art_content)
                    art_embedding = self.embedding_service.embed(art_content)
                    
                    artifacts.append(Artifact(
                        id=art_id,
                        type=art_type,
                        embedding=art_embedding,
                        hash=art_hash
                    ))
                
                # Recursively traverse (but skip steps as we already processed it)
                for key, value in node.items():
                    if key != "steps":  # Skip steps to avoid duplicate processing
                        traverse(value, f"{path}.{key}" if path else key)
            
            elif isinstance(node, list):
                for i, item in enumerate(node):
                    traverse(item, f"{path}[{i}]")
        
        # Only traverse if we didn't find artifacts in steps
        if not artifacts:
            traverse(run_tree)
        
        return artifacts
    
    def _upsert_reference(self, reference: Reference) -> str:
        """Upsert a Reference node."""
        with self.driver.session() as session:
            session.run("""
                MERGE (ref:Reference {id: $id})
                SET ref.type = $type,
                    ref.embedding = $embedding,
                    ref.source_ref = $source_ref
            """,
                id=reference.id,
                type=reference.type,
                embedding=reference.embedding,
                source_ref=reference.source_ref
            )
        return reference.id
    
    def _upsert_artifact(self, artifact: Artifact) -> str:
        """Upsert an Artifact node."""
        with self.driver.session() as session:
            session.run("""
                MERGE (a:Artifact {id: $id})
                SET a.type = $type,
                    a.embedding = $embedding,
                    a.hash = $hash
            """,
                id=artifact.id,
                type=artifact.type,
                embedding=artifact.embedding,
                hash=artifact.hash
            )
        return artifact.id
    
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

