"""LLM service for summarization and analysis."""
from typing import Dict, Any
import config


class LLMService:
    """Service for LLM operations like summarization."""
    
    def __init__(self):
        self.provider = config.Config.PROVIDER
        
        if self.provider == "gemini":
            try:
                import google.generativeai as genai
            except ImportError:
                raise ImportError("google-generativeai package is required for Gemini. Install with: pip install google-generativeai")
            
            if not config.Config.GEMINI_API_KEY:
                raise ValueError("GEMINI_API_KEY must be set when PROVIDER=gemini")
            genai.configure(api_key=config.Config.GEMINI_API_KEY)
            self.client = genai
            self.model = config.Config.GEMINI_CHAT_MODEL
        else:  # openai
            import openai
            if not config.Config.OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY must be set when PROVIDER=openai")
            self.client = openai.OpenAI(api_key=config.Config.OPENAI_API_KEY)
            self.model = config.Config.OPENAI_CHAT_MODEL
    
    def summarize_run(self, run_tree: Dict[str, Any], outcome: str) -> str:
        """
        Summarize an agent run focusing on references, artifacts, and workflow.
        
        Args:
            run_tree: The full run tree/map
            outcome: The outcome of the run (success/failure/partial)
            
        Returns:
            A 5-7 sentence summary
        """
        prompt = f"""Summarize this agent run in 5-7 sentences focusing on:

1. What information was referenced (documents, schemas, API responses, prior runs)
2. What was produced (schemas, plans, reports, code outputs)
3. The overall workflow shape
4. Why it succeeded or failed

Run outcome: {outcome}

Run tree:
{self._format_run_tree(run_tree)}

Provide a concise, structured summary that would help an agent understand what happened in this run and what was learned."""

        if self.provider == "gemini":
            # Gemini model names need 'models/' prefix for GenerativeModel
            model_name = self.model if self.model.startswith("models/") else f"models/{self.model}"
            model = self.client.GenerativeModel(model_name)
            response = model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.3,
                    "max_output_tokens": 500,
                }
            )
            return response.text.strip()
        else:  # openai
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that summarizes agent runs for knowledge base storage."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            return response.choices[0].message.content.strip()
    
    def _format_run_tree(self, run_tree: Dict[str, Any], indent: int = 0) -> str:
        """Format run tree for display in prompt."""
        lines = []
        prefix = "  " * indent
        
        for key, value in run_tree.items():
            if isinstance(value, dict):
                lines.append(f"{prefix}{key}:")
                lines.append(self._format_run_tree(value, indent + 1))
            elif isinstance(value, list):
                lines.append(f"{prefix}{key}: [list with {len(value)} items]")
                if value and isinstance(value[0], dict):
                    for i, item in enumerate(value[:3]):  # Limit to first 3 items
                        lines.append(f"{prefix}  [{i}]:")
                        lines.append(self._format_run_tree(item, indent + 2))
            else:
                # Truncate long values
                str_value = str(value)
                if len(str_value) > 200:
                    str_value = str_value[:200] + "..."
                lines.append(f"{prefix}{key}: {str_value}")
        
        return "\n".join(lines)
    
    def make_decision(self, prompt: str) -> str:
        """
        Make a memory admission decision using LLM.
        
        Args:
            prompt: The decision prompt
            
        Returns:
            JSON string with decision, target_run_id (optional), and reason
        """
        if self.provider == "gemini":
            model_name = self.model if self.model.startswith("models/") else f"models/{self.model}"
            model = self.client.GenerativeModel(model_name)
            try:
                # For Gemini, we can't force JSON via config, so we rely on the prompt
                # and parse the response carefully
                response = model.generate_content(
                    prompt,
                    generation_config={
                        "temperature": 0.1,  # Very low temperature for consistent JSON
                        "max_output_tokens": 200,
                    }
                )
                return response.text.strip()
            except Exception as e:
                error_str = str(e)
                # Check for rate limit errors
                if "429" in error_str or "quota" in error_str.lower() or "rate" in error_str.lower():
                    raise Exception(f"Gemini API rate limit exceeded. Please wait before retrying. Error: {error_str[:200]}")
                raise
        else:  # openai
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a memory curator for agent workflows. Respond with JSON only. No markdown, no code blocks."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=200,
                response_format={"type": "json_object"}  # Force JSON output
            )
            return response.choices[0].message.content.strip()

