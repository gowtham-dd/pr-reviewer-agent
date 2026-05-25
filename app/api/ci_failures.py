import uuid
from typing import Optional
from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel

from app.db import get_all_ci_failures, get_ci_failure
from app.core.ci_pipeline import run_ci_pipeline_task

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
