import os
import google.generativeai as genai
from src.config import Config
import json

def test_llm_connection():
    print("\n[1] Testing Gemini API Connection...")
    try:
        Config.validate()
        genai.configure(api_key=Config.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        print("    Sending test prompt...")
        response = model.generate_content("Return a JSON list of 1 technical skill from this text: 'I fixed the React useEffect hook dependency array.'", 
                                        generation_config={"response_mime_type": "application/json"})
        print(f"    Raw Response: {response.text}")
        parsed = json.loads(response.text)
        print(f"    Parsed JSON: {parsed}")
        return True
    except Exception as e:
        print(f"    [FAIL] LLM Error: {e}")
        print("    suggestion: Check GEMINI_API_KEY in .env or model availability.")
        return False

def test_tfidf_loading():
    print("\n[2] Testing TF-IDF Calculator...")
    from src.tfidf import TFIDFCalculator
    try:
        tfidf = TFIDFCalculator()
        tfidf.fit_corpus([{'files': [{'patch_content': '+ import react'}]}])
        w = tfidf.compute_weight('+ import react')
        print(f"    Weight for 'react': {w}")
        return True
    except Exception as e:
        print(f"    [FAIL] TF-IDF Error: {e}")
        return False

if __name__ == "__main__":
    print("=== System Diagnostics ===")
    llm_ok = test_llm_connection()
    tfidf_ok = test_tfidf_loading()
    
    if llm_ok and tfidf_ok:
        print("\n[SUCCESS] Core components are functional. The issue might be in MCTS logic or data fetching.")
    else:
        print("\n[FAILURE] Fix the errors above.")
