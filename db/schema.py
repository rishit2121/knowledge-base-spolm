"""Neo4j schema initialization and management.

Minimal schema (Task as spine):
- Task: semantic anchor (what the run is about)
- Run: one execution, leaf under Task
- (Run)-[:ABOUT_TASK]->(Task)
"""
from db.connection import get_neo4j_driver
import config


def initialize_schema() -> None:
    """
    Initialize Neo4j schema with Task and Run nodes, ABOUT_TASK relationship.
    Task = branch, Run = leaf. Tasks are extracted dynamically, not predefined.
    """
    driver = get_neo4j_driver()

    embed_config = config.Config.get_embedding_config()
    embedding_dimension = embed_config["dimension"]

    with driver.session() as session:
        try:
            # Task embedding index
            session.run(
                """
                CREATE VECTOR INDEX task_embedding_index IF NOT EXISTS
                FOR (t:Task)
                ON (t.embedding)
                OPTIONS {
                    indexConfig: {
                        `vector.dimensions`: $dimensions,
                        `vector.similarity_function`: 'cosine'
                    }
                }
            """,
                dimensions=embedding_dimension,
            )

            # Run embedding index
            session.run(
                """
                CREATE VECTOR INDEX run_embedding_index IF NOT EXISTS
                FOR (r:Run)
                ON (r.embedding)
                OPTIONS {
                    indexConfig: {
                        `vector.dimensions`: $dimensions,
                        `vector.similarity_function`: 'cosine'
                    }
                }
            """,
                dimensions=embedding_dimension,
            )

            print("✓ Vector indexes created successfully")

        except Exception as e:
            print(f"⚠ Vector indexes not supported: {e}")
            session.run("CREATE INDEX task_id_index IF NOT EXISTS FOR (t:Task) ON (t.id)")
            session.run("CREATE INDEX run_id_index IF NOT EXISTS FOR (r:Run) ON (r.id)")
            session.run("CREATE INDEX run_created_at_index IF NOT EXISTS FOR (r:Run) ON (r.created_at)")

        # Constraints
        try:
            session.run(
                "CREATE CONSTRAINT task_id_unique IF NOT EXISTS FOR (t:Task) REQUIRE t.id IS UNIQUE"
            )
            session.run(
                "CREATE CONSTRAINT run_id_unique IF NOT EXISTS FOR (r:Run) REQUIRE r.id IS UNIQUE"
            )
            print("✓ Constraints created successfully")
        except Exception as e:
            print(f"⚠ Some constraints may already exist: {e}")

        print("✓ Schema initialization complete")


def verify_schema() -> bool:
    """Verify that the schema is properly initialized."""
    driver = get_neo4j_driver()

    with driver.session() as session:
        indexes = session.run("SHOW INDEXES").data()
        index_names = [idx.get("name", "") for idx in indexes]
        has_indexes = any(
            any(x in name for x in ["task", "run"]) for name in index_names
        )
        return has_indexes
