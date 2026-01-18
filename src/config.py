import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    
    # Graph Construction Parameters
    MAX_REPOS = 30
    MAX_COMMITS = 100
    MAX_ISSUES = 50
    
    @classmethod
    def validate(cls):
        if not cls.GITHUB_TOKEN:
            raise ValueError("Missing GITHUB_TOKEN in environment variables.")
        if not cls.GEMINI_API_KEY:
            raise ValueError("Missing GEMINI_API_KEY in environment variables.")
