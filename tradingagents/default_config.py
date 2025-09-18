import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
# Look for .env file in the project root (parent directory of tradingagents)
project_root = Path(__file__).parent.parent
dotenv_path = project_root / ".env"
load_dotenv(dotenv_path)

DEFAULT_CONFIG = {
    "project_dir": os.path.abspath(os.path.join(os.path.dirname(__file__), ".")),
    "results_dir": os.getenv("TRADINGAGENTS_RESULTS_DIR", "./results"),
    "data_dir": "/Users/yluo/Documents/Code/ScAI/FR1-data",
    # API Keys
    "finnhub_api_key": os.getenv("FINNHUB_API_KEY"),
    "google_api_key": os.getenv("GOOGLE_API_KEY"),
    "data_cache_dir": os.path.join(
        os.path.abspath(os.path.join(os.path.dirname(__file__), ".")),
        "dataflows/data_cache",
    ),
    # LLM settings
    "llm_provider": "google",
    "deep_think_llm": "gemini-2.5-pro",
    "quick_think_llm": "gemini-2.5-pro",
    "backend_url": "https://generativelanguage.googleapis.com/v1",
    # Debate and discussion settings
    "max_debate_rounds": 1,
    "max_risk_discuss_rounds": 1,
    "max_recur_limit": 100,
    # Tool settings
    "online_tools": True,
}
