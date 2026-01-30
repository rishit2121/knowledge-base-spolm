"""LLM service for summarization and analysis."""
from typing import Dict, Any, Tuple
import json
import re
import config
import google.generativeai.types as genai_types


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
    
    def summarize_run(self, run_tree: Dict[str, Any], outcome: str) -> Tuple[str, str]:
        """
        Summarize an agent run for memory storage and produce "why added" bullet points.
        Summary: how well the run proceeded + important info for memory.
        why_added: 2-4 short reasons this run is valuable to store (what future agents can learn from).

        Returns:
            (summary_str, reason_added_str). reason_added_str is newline-separated bullet points.
        """
        prompt = f"""You are a summarizer for an agent run that will be stored in a knowledge graph. Output valid JSON only, with two keys:

1. "summary": One short paragraph (2-4 sentences) that includes:
   - How well the run proceeded (success/failure/partial, key metrics, notable issues or successes).
   - Important information for memory (key decisions, findings, errors, outputs, or patterns worth remembering for future runs).

2. "why_added": An array of 2-4 short bullet-point reasons explaining WHY this run is valuable to add to memory. These are the reasons a human would see when viewing "why was this run added?"—focus on the value of the run for future retrieval, e.g. "Successfully built a weather API with caching", "Demonstrated error-handling pattern for external APIs", "Useful reference for Node.js project setup". Do NOT mention "no similar runs" or decision logic; only the concrete value of this run.

Run outcome: {outcome}

Full run log:
{self._format_run_tree(run_tree)}

Output only a single JSON object, no markdown fences or preamble. Example format:
{{"summary": "The run succeeded...", "why_added": ["Reason one.", "Reason two.", "Reason three."]}}"""

        if self.provider == "gemini":
            model_name = self.model if self.model.startswith("models/") else f"models/{self.model}"
            model = self.client.GenerativeModel(model_name)
            response = model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.3,
                    "max_output_tokens": 1024,  # Increased to prevent truncation (summary + why_added array)
                }
            )
            raw = (response.text or "").strip()
        else:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant. Respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1024  # Increased to prevent truncation (summary + why_added array)
            )
            raw = response.choices[0].message.content.strip()

        summary, reason_added_str = self._parse_summary_response(raw)
        # Always print debug for reason_added to verify formatting
        import sys
        print(f"[DEBUG LLM] Raw response length: {len(raw)}", file=sys.stderr)
        print(f"[DEBUG LLM] Raw response (first 800 chars):\n{raw[:800]}", file=sys.stderr)
        print(f"[DEBUG LLM] Parsed summary length: {len(summary)}, reason_added length: {len(reason_added_str)}", file=sys.stderr)
        print(f"[DEBUG LLM] reason_added value:\n{repr(reason_added_str)}", file=sys.stderr)
        sys.stderr.flush()
        return summary, reason_added_str

    def _parse_summary_response(self, raw: str) -> Tuple[str, str]:
        """Parse LLM JSON response into summary and newline-separated why_added bullets. Always returns at least one reason_added bullet."""
        text = raw.strip() if raw else ""
        if not text:
            return "No summary generated.", "• Run added to memory for future retrieval."

        # Strip markdown code fence if present
        if text.startswith("```"):
            text = re.sub(r"^```\w*\n?", "", text)
            text = re.sub(r"\n?```\s*$", "", text).strip()
        # Try to extract JSON object (Gemini sometimes adds preamble)
        start = text.find("{")
        if start >= 0:
            end = text.rfind("}") + 1
            if end > start:
                text = text[start:end]

        summary = ""
        reason_added_str = ""
        try:
            data = json.loads(text)
            import sys
            print(f"[DEBUG PARSER] Successfully parsed JSON. Keys: {list(data.keys())}", file=sys.stderr)
            summary = (data.get("summary") or "").strip()
            why_list = data.get("why_added")
            print(f"[DEBUG PARSER] why_added type: {type(why_list)}, value: {repr(why_list)}", file=sys.stderr)
            if isinstance(why_list, list) and why_list:
                bullets = [
                    "• " + (str(x).strip().lstrip("•-* "))
                    for x in why_list
                    if str(x).strip()
                ]
                reason_added_str = "\n".join(bullets) if bullets else ""
                print(f"[DEBUG PARSER] Converted list to bullets: {repr(reason_added_str)}", file=sys.stderr)
            elif isinstance(why_list, str) and why_list.strip():
                # Single string: split by newlines or periods into bullets
                for line in why_list.replace("•", "\n").split("\n"):
                    line = line.strip().lstrip("•-* ")
                    if line:
                        reason_added_str += ("• " + line + "\n") if not reason_added_str else ("• " + line + "\n")
                reason_added_str = reason_added_str.strip()
                print(f"[DEBUG PARSER] Converted string to bullets: {repr(reason_added_str)}", file=sys.stderr)
            else:
                print(f"[DEBUG PARSER] why_added is empty or invalid: {repr(why_list)}", file=sys.stderr)
        except (json.JSONDecodeError, TypeError) as e:
            import sys
            print(f"[DEBUG PARSER] JSON parse failed: {type(e).__name__}: {str(e)}", file=sys.stderr)
            print(f"[DEBUG PARSER] Text that failed to parse: {repr(text[:500])}", file=sys.stderr)
            summary = text

        if not summary:
            summary = raw if raw else "No summary generated."
        # Explicit fallback: always provide at least one "why added" bullet
        if not reason_added_str.strip():
            first_sentence = summary.split(". ")[0].strip()
            if first_sentence and not first_sentence.endswith("."):
                first_sentence += "."
            reason_added_str = "• Run added to memory for future retrieval.\n• " + (first_sentence or "Summary stored for context.")
        return summary, reason_added_str
    
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
                # Disable safety filters to ensure we get the full response
                import google.generativeai.types as genai_types
                response = model.generate_content(
                    prompt,
                    generation_config={
                        "temperature": 0.1,  # Very low temperature for consistent JSON
                        "max_output_tokens": 1048,  # Increased significantly to ensure full JSON response
                    },
                    safety_settings=[
                        {"category": genai_types.HarmCategory.HARM_CATEGORY_HARASSMENT, "threshold": genai_types.HarmBlockThreshold.BLOCK_NONE},
                        {"category": genai_types.HarmCategory.HARM_CATEGORY_HATE_SPEECH, "threshold": genai_types.HarmBlockThreshold.BLOCK_NONE},
                        {"category": genai_types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT, "threshold": genai_types.HarmBlockThreshold.BLOCK_NONE},
                        {"category": genai_types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT, "threshold": genai_types.HarmBlockThreshold.BLOCK_NONE},
                    ]
                )
                # Handle different response formats from Gemini
                import sys
                print("\n" + "="*80, file=sys.stderr)
                print("[DEBUG] ========== GEMINI API RESPONSE ==========", file=sys.stderr)
                print(f"[DEBUG] Response type: {type(response)}", file=sys.stderr)
                print(f"[DEBUG] Has 'text' attr: {hasattr(response, 'text')}", file=sys.stderr)
                
                # Check for finish reason and safety blocks
                finish_reason = None
                safety_ratings = None
                if hasattr(response, 'candidates') and len(response.candidates) > 0:
                    candidate = response.candidates[0]
                    finish_reason = getattr(candidate, 'finish_reason', None)
                    safety_ratings = getattr(candidate, 'safety_ratings', None)
                    print(f"[DEBUG] Finish reason: {finish_reason}", file=sys.stderr)
                    print(f"[DEBUG] Safety ratings: {safety_ratings}", file=sys.stderr)
                    if finish_reason == 'MAX_TOKENS':
                        print(f"[WARNING] Response was truncated due to max_output_tokens!", file=sys.stderr)
                    elif finish_reason == 'SAFETY':
                        print(f"[WARNING] Response was blocked by safety filters!", file=sys.stderr)
                        if safety_ratings:
                            for rating in safety_ratings:
                                print(f"[DEBUG] Safety rating: {rating}", file=sys.stderr)
                
                # Extract text - ALWAYS use candidates first (response.text can be truncated)
                result = None
                # First try candidates (more reliable for full text)
                if hasattr(response, 'candidates') and len(response.candidates) > 0:
                    candidate = response.candidates[0]
                    print(f"[DEBUG] Using candidates[0] for text extraction", file=sys.stderr)
                    print(f"[DEBUG] Candidate type: {type(candidate)}", file=sys.stderr)
                    print(f"[DEBUG] Candidate attributes: {dir(candidate)}", file=sys.stderr)
                    
                    if hasattr(candidate, 'content'):
                        print(f"[DEBUG] Candidate has content: {type(candidate.content)}", file=sys.stderr)
                        if hasattr(candidate.content, 'parts') and len(candidate.content.parts) > 0:
                            # Get all parts, concatenate them
                            parts_text = []
                            print(f"[DEBUG] Found {len(candidate.content.parts)} parts", file=sys.stderr)
                            for i, part in enumerate(candidate.content.parts):
                                print(f"[DEBUG] Part {i} type: {type(part)}, has text: {hasattr(part, 'text')}", file=sys.stderr)
                                if hasattr(part, 'text'):
                                    part_text = part.text
                                    print(f"[DEBUG] Part {i} text length: {len(part_text) if part_text else 0}", file=sys.stderr)
                                    parts_text.append(part_text)
                                else:
                                    print(f"[DEBUG] Part {i} has no text attr, trying str(): {str(part)[:100]}", file=sys.stderr)
                                    parts_text.append(str(part))
                            result = ''.join(parts_text) if parts_text else None
                            print(f"[DEBUG] Extracted {len(parts_text)} parts, total length: {len(result) if result else 0}", file=sys.stderr)
                        else:
                            print(f"[DEBUG] No parts found, using str(candidate.content)", file=sys.stderr)
                            result = str(candidate.content)
                    else:
                        print(f"[DEBUG] Candidate has no content, using str(candidate)", file=sys.stderr)
                        result = str(candidate)
                
                # Fallback to response.text (but warn if it's different from candidates)
                if not result and hasattr(response, 'text'):
                    result = response.text
                    print(f"[WARNING] Using response.text (fallback) - candidates extraction failed", file=sys.stderr)
                elif hasattr(response, 'text') and result:
                    # Compare lengths
                    text_from_property = response.text
                    if len(text_from_property) != len(result):
                        print(f"[WARNING] response.text length ({len(text_from_property)}) != candidates length ({len(result)})", file=sys.stderr)
                        print(f"[WARNING] response.text: {text_from_property[:100]}", file=sys.stderr)
                        print(f"[WARNING] Using candidates result (longer/more complete)", file=sys.stderr)
                
                if not result:
                    result = str(response)
                    print(f"[DEBUG] Using str(response) (last resort)", file=sys.stderr)
                
                # Clean and validate
                if result:
                    result = result.strip()
                
                print(f"[DEBUG] Result type: {type(result)}", file=sys.stderr)
                print(f"[DEBUG] Result length: {len(str(result)) if result else 0}", file=sys.stderr)
                print(f"[DEBUG] Result is None: {result is None}", file=sys.stderr)
                print(f"[DEBUG] Result is empty: {not result or len(str(result)) == 0}", file=sys.stderr)
                print(f"[DEBUG] Full result content:\n{result}", file=sys.stderr)
                print(f"[DEBUG] First 200 chars: {str(result)[:200] if result else 'None'}", file=sys.stderr)
                print(f"[DEBUG] Last 200 chars: {str(result)[-200:] if result and len(str(result)) > 200 else str(result)}", file=sys.stderr)
                print("[DEBUG] ===========================================", file=sys.stderr)
                print("="*80 + "\n", file=sys.stderr)
                sys.stderr.flush()
                
                if not result or len(str(result)) == 0:
                    raise Exception("Gemini returned empty response")
                
                return result
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

