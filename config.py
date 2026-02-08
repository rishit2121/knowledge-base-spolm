"""Configuration management for the knowledge base system."""
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration."""
    
    # Neo4j Configuration
    NEO4J_URI: str = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USER: str = os.getenv("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD: str = os.getenv("NEO4J_PASSWORD", "")
    
    # Provider Configuration (openai or gemini)
    PROVIDER: str = os.getenv("PROVIDER", "openai").lower()
    
    # OpenAI Configuration
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_EMBEDDING_MODEL: str = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    OPENAI_CHAT_MODEL: str = os.getenv("OPENAI_CHAT_MODEL", "gpt-4-turbo-preview")
    
    # Gemini Configuration
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
    # Available embedding models: text-embedding-004, gemini-embedding-001, embedding-001
    GEMINI_EMBEDDING_MODEL: str = os.getenv("GEMINI_EMBEDDING_MODEL", "gemini-embedding-001")
    # Available chat models: gemini-2.5-flash, gemini-2.5-pro, gemini-2.0-flash
    GEMINI_CHAT_MODEL: str = os.getenv("GEMINI_CHAT_MODEL", "gemini-2.5-flash")
    
    # Embedding Configuration (provider-specific defaults)
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL")  # Override if set
    EMBEDDING_DIMENSION: int = int(os.getenv("EMBEDDING_DIMENSION", "1536"))  # OpenAI default
    
    # Similarity Configuration
    SIMILARITY_THRESHOLD: float = float(os.getenv("SIMILARITY_THRESHOLD", "0.85"))
    
    @classmethod
    def get_embedding_config(cls):
        """Get embedding configuration based on provider."""
        if cls.PROVIDER == "gemini":
            return {
                "model": cls.EMBEDDING_MODEL or cls.GEMINI_EMBEDDING_MODEL,
                "dimension": 768  # Gemini embeddings are 768 dimensions
            }
        else:  # openai
            return {
                "model": cls.EMBEDDING_MODEL or cls.OPENAI_EMBEDDING_MODEL,
                "dimension": cls.EMBEDDING_DIMENSION
            }
    
    # API Configuration
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))

    # CORS: comma-separated origins (e.g. http://localhost:3000,https://myapp.vercel.app). Required when allow_credentials=True.
    CORS_ORIGINS: str = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000,https://fancy-begonia-749ca6.netlify.app",
    )
    
    @classmethod
    def validate(cls) -> None:
        """Validate that required configuration is present."""
        if not cls.NEO4J_PASSWORD:
            raise ValueError("NEO4J_PASSWORD must be set")
        
        if cls.PROVIDER == "gemini":
            if not cls.GEMINI_API_KEY:
                raise ValueError("GEMINI_API_KEY must be set when PROVIDER=gemini")
        else:  # openai
            if not cls.OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY must be set when PROVIDER=openai")

