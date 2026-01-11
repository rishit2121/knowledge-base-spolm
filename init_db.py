"""Initialize the Neo4j database schema."""
import sys
from db.schema import initialize_schema, verify_schema
from db.connection import get_neo4j_driver, close_neo4j_driver
import config


def main():
    """Initialize the database schema."""
    print("Initializing Knowledge Base schema...")
    print(f"Connecting to Neo4j at {config.Config.NEO4J_URI}")
    
    try:
        # Validate configuration
        config.Config.validate()
        
        # Test connection
        driver = get_neo4j_driver()
        with driver.session() as session:
            result = session.run("RETURN 1 AS test")
            result.single()
        print("✓ Connected to Neo4j")
        
        # Initialize schema
        initialize_schema()
        
        # Verify schema
        if verify_schema():
            print("✓ Schema verification passed")
        else:
            print("⚠ Schema verification had issues, but continuing...")
        
        print("\n✓ Database initialization complete!")
        print("\nYou can now:")
        print("  1. Start the API: python api.py")
        print("  2. Process runs via POST /runs")
        print("  3. Retrieve memory via POST /retrieve")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)
    finally:
        close_neo4j_driver()


if __name__ == "__main__":
    main()

