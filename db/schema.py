"""Neo4j schema initialization and management."""
from neo4j import Driver
from db.connection import get_neo4j_driver
import config


def initialize_schema() -> None:
    """
    Initialize Neo4j schema with nodes, relationships, and vector indexes.
    This should be run once when setting up the knowledge base.
    """
    driver = get_neo4j_driver()
    
    # Get correct embedding dimension based on provider
    embed_config = config.Config.get_embedding_config()
    embedding_dimension = embed_config["dimension"]
    
    with driver.session() as session:
        # Create vector indexes for similarity search
        # Note: Vector indexes require Neo4j 5.11+ with vector index support
        # For older versions, you may need to use full-text indexes or manual similarity
        
        try:
            # Task embedding index
            session.run("""
                CREATE VECTOR INDEX task_embedding_index IF NOT EXISTS
                FOR (t:Task)
                ON (t.embedding)
                OPTIONS {
                    indexConfig: {
                        `vector.dimensions`: $dimensions,
                        `vector.similarity_function`: 'cosine'
                    }
                }
            """, dimensions=embedding_dimension)
            
            # Run embedding index
            session.run("""
                CREATE VECTOR INDEX run_embedding_index IF NOT EXISTS
                FOR (r:Run)
                ON (r.embedding)
                OPTIONS {
                    indexConfig: {
                        `vector.dimensions`: $dimensions,
                        `vector.similarity_function`: 'cosine'
                    }
                }
            """, dimensions=embedding_dimension)
            
            # Reference embedding index
            session.run("""
                CREATE VECTOR INDEX reference_embedding_index IF NOT EXISTS
                FOR (ref:Reference)
                ON (ref.embedding)
                OPTIONS {
                    indexConfig: {
                        `vector.dimensions`: $dimensions,
                        `vector.similarity_function`: 'cosine'
                    }
                }
            """, dimensions=embedding_dimension)
            
            # Artifact embedding index
            session.run("""
                CREATE VECTOR INDEX artifact_embedding_index IF NOT EXISTS
                FOR (a:Artifact)
                ON (a.embedding)
                OPTIONS {
                    indexConfig: {
                        `vector.dimensions`: $dimensions,
                        `vector.similarity_function`: 'cosine'
                    }
                }
            """, dimensions=embedding_dimension)
            
            print("✓ Vector indexes created successfully")
            
        except Exception as e:
            # Fallback for Neo4j versions without vector index support
            print(f"⚠ Vector indexes not supported, using fallback: {e}")
            print("  Consider using Neo4j 5.11+ or Aura for vector index support")
            
            # Create regular indexes as fallback
            session.run("CREATE INDEX task_id_index IF NOT EXISTS FOR (t:Task) ON (t.id)")
            session.run("CREATE INDEX run_id_index IF NOT EXISTS FOR (r:Run) ON (r.id)")
            session.run("CREATE INDEX reference_id_index IF NOT EXISTS FOR (ref:Reference) ON (ref.id)")
            session.run("CREATE INDEX artifact_id_index IF NOT EXISTS FOR (a:Artifact) ON (a.id)")
            session.run("CREATE INDEX run_created_at_index IF NOT EXISTS FOR (r:Run) ON (r.created_at)")
            session.run("CREATE INDEX outcome_label_index IF NOT EXISTS FOR (o:Outcome) ON (o.label)")
        
        # Create constraints for uniqueness
        try:
            session.run("CREATE CONSTRAINT task_id_unique IF NOT EXISTS FOR (t:Task) REQUIRE t.id IS UNIQUE")
            session.run("CREATE CONSTRAINT run_id_unique IF NOT EXISTS FOR (r:Run) REQUIRE r.id IS UNIQUE")
            session.run("CREATE CONSTRAINT reference_id_unique IF NOT EXISTS FOR (ref:Reference) REQUIRE ref.id IS UNIQUE")
            session.run("CREATE CONSTRAINT artifact_id_unique IF NOT EXISTS FOR (a:Artifact) REQUIRE a.id IS UNIQUE")
            # Outcome nodes use label as identifier, so we create a constraint on label
            session.run("CREATE CONSTRAINT outcome_label_unique IF NOT EXISTS FOR (o:Outcome) REQUIRE o.label IS UNIQUE")
            print("✓ Constraints created successfully")
        except Exception as e:
            print(f"⚠ Some constraints may already exist: {e}")
        
        print("✓ Schema initialization complete")


def verify_schema() -> bool:
    """Verify that the schema is properly initialized."""
    driver = get_neo4j_driver()
    
    with driver.session() as session:
        # Check if indexes exist
        indexes = session.run("SHOW INDEXES").data()
        index_names = [idx.get("name", "") for idx in indexes]
        
        required_indexes = [
            "task_embedding_index",
            "run_embedding_index",
            "reference_embedding_index",
            "artifact_embedding_index"
        ]
        
        # Check if at least some indexes exist (vector or fallback)
        has_indexes = any(
            any(req in name for req in ["task", "run", "reference", "artifact"])
            for name in index_names
        )
        
        return has_indexes

