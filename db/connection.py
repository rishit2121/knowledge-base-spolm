"""Neo4j database connection management."""
from typing import Optional
from neo4j import GraphDatabase, Driver
import config

_driver: Optional[Driver] = None


def get_neo4j_driver() -> Driver:
    """Get or create Neo4j driver instance."""
    global _driver
    if _driver is None:
        _driver = GraphDatabase.driver(
            config.Config.NEO4J_URI,
            auth=(config.Config.NEO4J_USER, config.Config.NEO4J_PASSWORD)
        )
    return _driver


def close_neo4j_driver() -> None:
    """Close Neo4j driver connection."""
    global _driver
    if _driver is not None:
        _driver.close()
        _driver = None

