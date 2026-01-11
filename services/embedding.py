"""Embedding service for generating vector embeddings."""
from typing import List
import config


class EmbeddingService:
    """Service for generating embeddings using OpenAI or Gemini."""
    
    def __init__(self):
        self.provider = config.Config.PROVIDER
        embed_config = config.Config.get_embedding_config()
        self.model = embed_config["model"]
        self.dimension = embed_config["dimension"]
        
        if self.provider == "gemini":
            try:
                import google.generativeai as genai
            except ImportError:
                raise ImportError("google-generativeai package is required for Gemini. Install with: pip install google-generativeai")
            
            if not config.Config.GEMINI_API_KEY:
                raise ValueError("GEMINI_API_KEY must be set when PROVIDER=gemini")
            genai.configure(api_key=config.Config.GEMINI_API_KEY)
            self.client = genai
        else:  # openai
            import openai
            if not config.Config.OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY must be set when PROVIDER=openai")
            self.client = openai.OpenAI(api_key=config.Config.OPENAI_API_KEY)
    
    def embed(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        
        if self.provider == "gemini":
            # Gemini model names need 'models/' prefix
            model_name = self.model if self.model.startswith("models/") else f"models/{self.model}"
            result = self.client.embed_content(
                model=model_name,
                content=text.strip()
            )
            # Gemini returns embedding as a list directly in 'embedding' field
            return result['embedding']
        else:  # openai
            response = self.client.embeddings.create(
                model=self.model,
                input=text.strip()
            )
            return response.data[0].embedding
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        if not texts:
            return []
        
        # Filter out empty texts
        valid_texts = [t.strip() for t in texts if t and t.strip()]
        if not valid_texts:
            return []
        
        if self.provider == "gemini":
            # Gemini handles batch embeddings
            # Gemini model names need 'models/' prefix
            model_name = self.model if self.model.startswith("models/") else f"models/{self.model}"
            embeddings = []
            for text in valid_texts:
                result = self.client.embed_content(
                    model=model_name,
                    content=text
                )
                embeddings.append(result['embedding'])
            return embeddings
        else:  # openai
            response = self.client.embeddings.create(
                model=self.model,
                input=valid_texts
            )
            return [item.embedding for item in response.data]

