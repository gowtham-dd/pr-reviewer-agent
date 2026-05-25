from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

from app.api.reviews import router as reviews_router
from app.api.settings import router as settings_router
from app.api.webhook import router as webhook_router
from app.api.ci_failures import router as ci_router

app = FastAPI(
    title="AI Automated Code Review Pipeline",
    description="LangGraph-powered automated Pull Request reviews with a Human-in-the-Loop approval gate.",
    version="1.0.0"
)

# Enable CORS for local testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(reviews_router)
app.include_router(settings_router)
app.include_router(webhook_router)
app.include_router(ci_router)

# --- Web UI Endpoint ---

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    """Serves the highly polished, modern web dashboard."""
    print("🖥️  [Dashboard] Serving dashboard UI to client browser...")
    from app.templates import DASHBOARD_HTML
    return DASHBOARD_HTML
