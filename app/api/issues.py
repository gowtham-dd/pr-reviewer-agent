from typing import Optional
from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel

from app.db import get_all_issues, get_issue
from app.core.issues_pipeline import run_issues_pipeline_task

class ManualIssuePayload(BaseModel):
    issue_number: int
    issue_title: str
    issue_body: Optional[str] = ""
    repo_name: str
    author: str
    branch: Optional[str] = "main"

router = APIRouter(prefix="/api/issues", tags=["GitHub Issues"])

@router.get("")
async def api_get_issues():
    """Retrieve history of all analyzed GitHub Issues."""
    return get_all_issues()

@router.get("/{issue_id}")
async def api_get_issue(issue_id: str):
    """Retrieve details of a specific analyzed GitHub Issue."""
    issue = get_issue(issue_id)
    if not issue:
        raise HTTPException(status_code=404, detail="GitHub Issue report not found")
    return issue

@router.post("/analyze")
async def api_analyze_issue(payload: ManualIssuePayload, background_tasks: BackgroundTasks):
    """
    Exposes an API to manually submit an issue for critical status classification
    and remedy extraction.
    """
    issue_id = f"issue-{payload.repo_name.replace('/', '-')}-{payload.issue_number}"
    background_tasks.add_task(
        run_issues_pipeline_task,
        issue_id,
        payload.issue_number,
        payload.issue_title,
        payload.issue_body,
        payload.repo_name,
        payload.author,
        None,  # No installation ID for manual test triggers
        payload.branch or "main"
    )
    return {"status": "accepted", "issue_id": issue_id}
