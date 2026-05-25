import os
import re
import asyncio
from typing import Optional
from langchain_core.messages import SystemMessage, HumanMessage
from app.config import get_settings

# Prevent concurrent API rate limits (HTTP 429) on model endpoints
LLM_SEMAPHORE = asyncio.Semaphore(1)


def get_chat_model():
    cfg = get_settings()
    provider = cfg.llm_provider.lower()
    
    if provider == "openai" and cfg.openai_api_key:
        from langchain_openai import ChatOpenAI
        model = cfg.llm_model or "gpt-4o-mini"
        return ChatOpenAI(api_key=cfg.openai_api_key, model=model, temperature=0.2)
        
    elif provider == "gemini" and cfg.gemini_api_key:
        from langchain_google_genai import ChatGoogleGenerativeAI
        model = cfg.llm_model or "gemini-2.5-flash"
        return ChatGoogleGenerativeAI(google_api_key=cfg.gemini_api_key, model=model, temperature=0.2)
        
    elif provider == "anthropic" and cfg.anthropic_api_key:
        from langchain_anthropic import ChatAnthropic
        model = cfg.llm_model or "claude-3-5-sonnet-20241022"
        return ChatAnthropic(api_key=cfg.anthropic_api_key, model_name=model, temperature=0.2)
        
    elif provider == "groq" and cfg.groq_api_key:
        from langchain_groq import ChatGroq
        model = cfg.llm_model or "llama-3.3-70b-versatile"
        return ChatGroq(api_key=cfg.groq_api_key, model_name=model, temperature=0.2)
        
    else:
        # Fallback / Not Configured
        return None

async def call_llm(system_prompt: str, user_prompt: str) -> str:
    """
    Calls the configured LLM.
    Includes parallel rate-limit handling and automatic retries.
    """
    model = get_chat_model()
    if model is None:
        raise ValueError(
            "LLM model could not be initialized. Please check that LLM_PROVIDER is configured "
            "correctly and that the corresponding API key (e.g. GEMINI_API_KEY, OPENAI_API_KEY) is set."
        )

    async with LLM_SEMAPHORE:
        max_retries = 3
        backoff = 2.0
        for attempt in range(max_retries):
            try:
                messages = [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=user_prompt)
                ]
                response = await model.ainvoke(messages)
                return response.content
            except Exception as e:
                # Detect rate limit 429 errors
                err_msg = str(e).lower()
                if "429" in err_msg or "rate limit" in err_msg:
                    if attempt < max_retries - 1:
                        print(f"⚠️ [LLM API Rate Limited] Retrying in {backoff}s (Attempt {attempt+1}/{max_retries})...")
                        await asyncio.sleep(backoff)
                        backoff *= 2.0
                        continue
                
                # Raise error if retries are exhausted or it's a different issue
                print(f"❌ [LLM API Error] Call failed on attempt {attempt+1}: {e}")
                if attempt == max_retries - 1:
                    raise e
