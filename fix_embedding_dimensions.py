"""Fix embedding dimension mismatch by dropping and recreating vector indexes."""
from db.connection import get_neo4j_driver
import config


def fix_embedding_dimensions():
    """Drop existing vector indexes and recreate with correct dimensions."""
    driver = get_neo4j_driver()
    
    # Get correct embedding dimension based on current provider
    embed_config = config.Config.get_embedding_config()
    embedding_dimension = embed_config["dimension"]
    
    print(f"🔧 Fixing embedding dimensions...")
    print(f"   Provider: {config.Config.PROVIDER}")
    print(f"   Model: {embed_config['model']}")
    print(f"   Dimension: {embedding_dimension}")
    print()
    
    with driver.session() as session:
        # Drop existing vector indexes (Task and Run only in minimal schema)
        indexes_to_drop = [
            "task_embedding_index",
            "run_embedding_index",
            "reference_embedding_index",  # Legacy
            "artifact_embedding_index",   # Legacy
        ]
        
        print("🗑️  Dropping existing vector indexes...")
        for index_name in indexes_to_drop:
            try:
                session.run(f"DROP INDEX {index_name} IF EXISTS")
                print(f"   ✓ Dropped {index_name}")
            except Exception as e:
                print(f"   ⚠ Could not drop {index_name}: {e}")
        
        print()
        print("🔨 Creating new vector indexes with correct dimensions...")
        
        # Create new indexes with correct dimension
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
            print(f"   ✓ Created task_embedding_index (dimension: {embedding_dimension})")
            
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
            print(f"   ✓ Created run_embedding_index (dimension: {embedding_dimension})")

            print()
            print("✅ Vector indexes recreated successfully!")
            print()
            
            # Clear existing embeddings with wrong dimensions
            print("🧹 Clearing existing embeddings with wrong dimensions...")
            try:
                result = session.run("""
                    MATCH (n)
                    WHERE n.embedding IS NOT NULL
                    SET n.embedding = null
                    RETURN count(n) AS cleared_count
                """)
                record = result.single()
                cleared_count = record["cleared_count"] if record else 0
                print(f"   ✓ Cleared {cleared_count} embeddings")
                print()
                print("✅ All embeddings cleared. New runs will create embeddings with correct dimensions.")
            except Exception as e:
                print(f"   ⚠ Could not clear embeddings: {e}")
                print("   You may need to clear them manually in Neo4j Browser:")
                print("   MATCH (n) WHERE n.embedding IS NOT NULL SET n.embedding = null")
            
        except Exception as e:
            print(f"❌ Error creating indexes: {e}")
            raise


if __name__ == "__main__":
    config.Config.validate()
    fix_embedding_dimensions()

