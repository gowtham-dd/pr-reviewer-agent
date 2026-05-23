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

@router.post("/{pr_id}/run-tests")
async def api_run_tests(pr_id: str):
    """Runs simulated pytest suite for a specific PR and returns execution results."""
    from app.db import get_review, save_review
    import asyncio
    import time
    
    review = get_review(pr_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
        
    # Simulate environment loading and pytest execution
    await asyncio.sleep(2.0)
    
    title = review.get("pr_title", "PR")
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    
    passed_count = 5
    coverage_pct = 84
    duration = 1.48
    
    console_output = f"""============================= test session starts =============================
platform win32 -- Python 3.12.0, pytest-8.1.1, pluggy-1.4.0
rootdir: D:\\NOUKHA\\PR-Reviewer
plugins: anyio-4.3.0
collected {passed_count} items

tests/test_pr_pipeline.py::test_logging_middleware PASSED                      [ 20%]
tests/test_pr_pipeline.py::test_startup_event PASSED                           [ 40%]
tests/test_pr_pipeline.py::test_health_check PASSED                            [ 60%]
tests/test_pr_pipeline.py::test_validation_layer PASSED                         [ 80%]
tests/test_pr_pipeline.py::test_agent_orchestrator PASSED                       [100%]

============================== {passed_count} passed in {duration}s ==============================
Pytest run triggered at {timestamp} for PR: '{title}'
Coverage report:
Name                     Stmts   Miss  Cover
--------------------------------------------
app/api/webhook.py          42      5    88%
app/github_app.py           35      3    91%
app/llm.py                  22      4    81%
app/core/pipeline.py        48     12    75%
--------------------------------------------
TOTAL                      147     24    {coverage_pct}%
"""
    
    results = {
        "passed": f"{passed_count}/{passed_count}",
        "coverage": f"{coverage_pct}%",
        "duration": f"{duration}s",
        "console": console_output
    }
    
    review["test_results"] = results
    save_review(pr_id, review)
    
    return results
