import uuid
from typing import Optional
from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel

from app.db import get_all_reviews, get_review
from app.core.pipeline import run_pipeline_task, resume_pipeline_task

router = APIRouter(prefix="/api/reviews", tags=["Reviews"])

class TriggerReviewRequest(BaseModel):
    pr_title: str
    repo_name: str
    author: str
    diff: str

class ApprovalRequest(BaseModel):
    feedback: Optional[str] = ""

@router.get("")
async def api_get_reviews():
    """Retrieve history of all code reviews."""
    return get_all_reviews()

@router.get("/{pr_id}")
async def api_get_review(pr_id: str):
    """Retrieve details of a specific code review."""
    review = get_review(pr_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return review

@router.post("/mock-trigger")
async def api_mock_trigger(req: TriggerReviewRequest, background_tasks: BackgroundTasks):
    """Triggers a local mock PR review without requiring an active GitHub webhook."""
    pr_id = f"mock-{uuid.uuid4().hex[:6]}"
    background_tasks.add_task(
        run_pipeline_task,
        pr_id,
        req.pr_title,
        req.repo_name,
        req.author,
        req.diff
    )
    return {"status": "accepted", "pr_id": pr_id}

@router.post("/{pr_id}/approve")
async def api_approve_review(pr_id: str, req: ApprovalRequest, background_tasks: BackgroundTasks):
    """Approve review report and resume the publisher node."""
    review = get_review(pr_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    if review["status"] != "pending":
        raise HTTPException(status_code=400, detail="Review is not pending approval")
        
    background_tasks.add_task(resume_pipeline_task, pr_id, "approved", req.feedback)
    return {"status": "processing", "decision": "approved"}

@router.post("/{pr_id}/reject")
async def api_reject_review(pr_id: str, req: ApprovalRequest, background_tasks: BackgroundTasks):
    """Reject a review and close the LangGraph checkpointer."""
    review = get_review(pr_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    if review["status"] != "pending":
        raise HTTPException(status_code=400, detail="Review is not pending approval")
        
    background_tasks.add_task(resume_pipeline_task, pr_id, "rejected", req.feedback)
    return {"status": "processing", "decision": "rejected"}
