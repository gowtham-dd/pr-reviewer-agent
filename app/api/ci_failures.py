import uuid
from typing import Optional
from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel

from app.db import get_all_ci_failures, get_ci_failure
from app.core.ci_pipeline import run_ci_pipeline_task

class CIFailurePayload(BaseModel):
    workflow_id: str
    repo_name: str
    failed_step: str
    raw_logs: str
    commit_sha: Optional[str] = None
    branch: Optional[str] = "main"

router = APIRouter(prefix="/api/ci", tags=["CI/CD Failures"])

@router.get("")
async def api_get_ci_failures():
    """Retrieve history of all CI/CD failure analysis reports."""
    return get_all_ci_failures()

@router.get("/{workflow_id}")
async def api_get_ci_failure(workflow_id: str):
    """Retrieve details of a specific CI/CD failure analysis report."""
    failure = get_ci_failure(workflow_id)
    if not failure:
        raise HTTPException(status_code=404, detail="CI Failure report not found")
    return failure

@router.post("/report-failure")
async def report_ci_failure(payload: CIFailurePayload, background_tasks: BackgroundTasks):
    """
    Exposes a production API to submit CI/CD pipeline or deployment failures.
    Triggers log pre-processing, AI diagnostics, and autonomous self-healing.
    """
    background_tasks.add_task(
        run_ci_pipeline_task,
        payload.workflow_id,
        payload.repo_name,
        payload.failed_step,
        payload.raw_logs,
        None,
        payload.commit_sha,
        payload.branch
    )
    return {"status": "accepted", "workflow_id": payload.workflow_id}

