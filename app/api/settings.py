import os
from typing import Optional
from fastapi import APIRouter
from pydantic import BaseModel

from app.config import get_settings

router = APIRouter(prefix="/api/settings", tags=["Settings"])

class SettingsRequest(BaseModel):
    llm_provider: str
    openai_api_key: Optional[str] = ""
    gemini_api_key: Optional[str] = ""
    anthropic_api_key: Optional[str] = ""
    groq_api_key: Optional[str] = ""
    llm_model: Optional[str] = ""
    teams_webhook_url: Optional[str] = ""

@router.get("")
async def api_get_settings():
    """Retrieve system settings."""
    cfg = get_settings()
    return {
        "llm_provider": cfg.llm_provider,
        "openai_api_key": "***" if cfg.openai_api_key else "",
        "gemini_api_key": "***" if cfg.gemini_api_key else "",
        "anthropic_api_key": "***" if cfg.anthropic_api_key else "",
        "groq_api_key": "***" if cfg.groq_api_key else "",
        "llm_model": cfg.llm_model,
        "teams_webhook_url": cfg.teams_webhook_url,
        "github_webhook_secret": cfg.github_webhook_secret
    }

@router.post("")
async def api_update_settings(req: SettingsRequest):
    """Updates runtime configuration settings."""
    cfg = get_settings()
    cfg.llm_provider = req.llm_provider
    if req.openai_api_key and req.openai_api_key != "***":
        cfg.openai_api_key = req.openai_api_key
    if req.gemini_api_key and req.gemini_api_key != "***":
        cfg.gemini_api_key = req.gemini_api_key
    if req.anthropic_api_key and req.anthropic_api_key != "***":
        cfg.anthropic_api_key = req.anthropic_api_key
    if req.groq_api_key and req.groq_api_key != "***":
        cfg.groq_api_key = req.groq_api_key
    cfg.llm_model = req.llm_model
    cfg.teams_webhook_url = req.teams_webhook_url
    
    # Update environment variables in-memory for LangChain components
    os.environ["LLM_PROVIDER"] = cfg.llm_provider
    if cfg.openai_api_key:
        os.environ["OPENAI_API_KEY"] = cfg.openai_api_key
    if cfg.gemini_api_key:
        os.environ["GEMINI_API_KEY"] = cfg.gemini_api_key
    if cfg.anthropic_api_key:
        os.environ["ANTHROPIC_API_KEY"] = cfg.anthropic_api_key
    if cfg.groq_api_key:
        os.environ["GROQ_API_KEY"] = cfg.groq_api_key
        
    return {"status": "success", "settings": await api_get_settings()}
