"""Clear all data from Neo4j database."""
import sys
from db.connection import get_neo4j_driver, close_neo4j_driver
import config


def clear_database():
    """Delete all nodes and relationships from Neo4j."""
    print("⚠️  WARNING: This will DELETE ALL DATA from your Neo4j database!")
    print(f"   Database: {config.Config.NEO4J_URI}")
    print()
    
    # Ask for confirmation
    response = input("Are you sure you want to delete ALL data? Type 'yes' to confirm: ")
    if response.lower() != 'yes':
        print("❌ Operation cancelled.")
        return False
    
    try:
        # Validate configuration
        config.Config.validate()
        
        # Test connection
        driver = get_neo4j_driver()
        with driver.session() as session:
            result = session.run("RETURN 1 AS test")
            result.single()
        print("✓ Connected to Neo4j")
        
        # Delete all nodes and relationships
        print("\n🗑️  Deleting all nodes and relationships...")
        with driver.session() as session:
            # Delete all relationships first
            result = session.run("MATCH ()-[r]->() DELETE r")
            deleted_rels = result.consume().counters.relationships_deleted
            print(f"   Deleted {deleted_rels} relationships")
            
            # Delete all nodes
            result = session.run("MATCH (n) DELETE n")
            deleted_nodes = result.consume().counters.nodes_deleted
            print(f"   Deleted {deleted_nodes} nodes")
        
        print("\n✅ Database cleared successfully!")
        print("\nNext steps:")
        print("  1. Run: python init_db.py  (to recreate schema)")
        print("  2. Start adding runs with the new User-Agent-Run structure")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        close_neo4j_driver()


def main():
    """Main function."""
    print("="*70)
    print("CLEAR NEO4J DATABASE")
    print("="*70)
    print()
    
    success = clear_database()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

