"""Neo4j database connection management."""
from typing import Optional
from neo4j import GraphDatabase, Driver
import config

_driver: Optional[Driver] = None


def get_neo4j_driver() -> Driver:
    """Get or create Neo4j driver instance."""
    global _driver
    if _driver is None:
        # Debug: Log the URI being used (mask password)
        uri = config.Config.NEO4J_URI
        import sys
        print(f"[DEBUG] Connecting to Neo4j URI: {uri}", file=sys.stderr)
        print(f"[DEBUG] Neo4j User: {config.Config.NEO4J_USER}", file=sys.stderr)
        sys.stderr.flush()
        
        _driver = GraphDatabase.driver(
            uri,
            auth=(config.Config.NEO4J_USER, config.Config.NEO4J_PASSWORD)
        )
    return _driver


def close_neo4j_driver() -> None:
    """Close Neo4j driver connection."""
    global _driver
    if _driver is not None:
        _driver.close()
        _driver = None

