import google.generativeai as genai
import json
from .config import Config

class LLMClient:
    """
    Interface for the Gemini Model to act as the Policy Network in MCTS.
    """
    def __init__(self):
        Config.validate()
        genai.configure(api_key=Config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        
    def infer_skills(self, node_context: dict, reasoning_path: list[str] = None) -> list[dict]:
        """
        Predicts skills based on the provided node context and the Reasoning Path.
        Returns a list of dicts: [{'skill': 'Name', 'confidence': 0.8, 'causal_link': '...'}]
        """
        import time

        prompt = self._construct_prompt(node_context, reasoning_path)
        
        # Retry Logic for Rate Limits (429)
        max_retries = 3
        backoff = 60 # Seconds
        
        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(prompt)
                # Basic cleanup for Markdown code blocks if model adds them
                clean_text = response.text.strip()
                if clean_text.startswith("```json"):
                    clean_text = clean_text[7:]
                if clean_text.startswith("```"):
                    clean_text = clean_text[3:]
                if clean_text.endswith("```"):
                    clean_text = clean_text[:-3]
                    
                result = json.loads(clean_text)
                return result # Success
                
            except Exception as e:
                error_str = str(e)
                if "429" in error_str or "quota" in error_str.lower():
                    print(f"    [LLM] Rate Limit Hit. Sleeping {backoff}s (Attempt {attempt+1}/{max_retries})...")
                    time.sleep(backoff)
                    backoff *= 1.5 # Exponential backoff if needed (though 60s should handle per-minute quota)
                else:
                    print(f"LLM Inference Error: {e}")
                    return [] # Non-retryable error
        
        print("    [LLM] Max retries exceeded.")
        return []

    def _construct_prompt(self, context: dict, path: list[str] = None) -> str:
        path_str = " -> ".join(path) if path else "Direct Exploration"
        
        intro = (
            f"You are a Senior CTO performing Deep Graph Reasoning to build a Developer Skill Profile.\n\n"
            f"REASONING PATH (Context):\n{path_str}\n\n"
            f"TARGET EVIDENCE:\n"
            f"Type: {context.get('type')}\n"
            f"Metadata: {context.get('message') or context.get('description')}\n"
            f"Data: {context.get('diff_summary') or str(context.get('topics'))}\n\n"
            
            f"TASK:\n"
            f"Using the full RESONING PATH as context, identify 1-3 TECHNICAL Hard Skills proven by this TARGET EVIDENCE.\n"
            f"Examples: 'Python', 'Vector Databases', 'Transformers', 'Dempster-Shafer Theory', 'FastAPI'.\n\n"
            
            f"CONSTRAINTS (STRICT):\n"
            f"1. IGNORE non-code skills (Markdown, Documentation, Writing, Readme updates).\n"
            f"2. IGNORE generic concepts (GitHub, VC, Agile).\n"
            f"3. Return ONLY Hard Technical Skills (Languages, Frameworks, Libraries, Algorithms).\n"
            f"4. CAUSALITY: Explain exactly HOW this specific file/commit proves the skill in the 'causal_link' field.\n\n"
            
            f"Return a JSON list: [{{'skill': 'Name', 'confidence': 0.0-1.0, 'causal_link': '...'}}]"
        )
        return intro
