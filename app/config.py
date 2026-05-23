import os
from typing import Optional
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

class AppSettings(BaseModel):
    # LLM Settings
    llm_provider: str = os.getenv("LLM_PROVIDER", "mock")  # mock, openai, gemini, anthropic, groq
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    gemini_api_key: Optional[str] = os.getenv("GEMINI_API_KEY")
    anthropic_api_key: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    groq_api_key: Optional[str] = os.getenv("GROQ_API_KEY")
    llm_model: Optional[str] = os.getenv("LLM_MODEL")

    # GitHub Settings
    github_app_id: Optional[str] = os.getenv("GITHUB_APP_ID")
    github_private_key: Optional[str] = os.getenv("GITHUB_PRIVATE_KEY")
    github_installation_id: Optional[str] = os.getenv("GITHUB_INSTALLATION_ID")
    github_webhook_secret: str = os.getenv("GITHUB_WEBHOOK_SECRET", "super-secret-key-123")
    github_token: Optional[str] = os.getenv("GITHUB_TOKEN")

    # Notification Settings
    teams_webhook_url: Optional[str] = os.getenv("TEAMS_WEBHOOK_URL")
    
    # Storage / DB (Local mock for now)
    db_path: str = os.getenv("DB_PATH", "reviews.json")

settings = AppSettings()

def get_settings() -> AppSettings:
    return settings
