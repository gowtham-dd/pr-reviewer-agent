import json
import zipfile
import io
import httpx
from typing import Optional
from fastapi import APIRouter, Request, Header, HTTPException, BackgroundTasks

from app.config import get_settings
from app.webhook import verify_signature
from app.core.pipeline import run_pipeline_task
from app.core.ci_pipeline import run_ci_pipeline_task
from app.core.issues_pipeline import run_issues_pipeline_task

router = APIRouter(tags=["Webhooks"])

async def fetch_github_workflow_logs(repo_name: str, run_id: int, token: str) -> str:
    """Helper to fetch and unzip raw workflow logs from GitHub API."""
    url = f"https://api.github.com/repos/{repo_name}/actions/runs/{run_id}/logs"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "PR-Reviewer-Agent"
    }
    print(f"🔗 [Webhook Actions Logs] Downloading zip archive from: {url}")
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(url, headers=headers, follow_redirects=True, timeout=15.0)
            if res.status_code != 200:
                print(f"❌ [Webhook Actions Logs] GitHub API returned status {res.status_code}: {res.text}")
                return f"Failed to download workflow logs: HTTP {res.status_code}"
            
            log_contents = []
            with zipfile.ZipFile(io.BytesIO(res.content)) as z:
                for name in z.namelist():
                    if name.endswith(".txt") or name.endswith(".log"):
                        with z.open(name) as log_file:
                            content = log_file.read().decode("utf-8", errors="ignore")
                            log_contents.append(f"=== Log File: {name} ===\n{content}")
            return "\n\n".join(log_contents)
    except Exception as e:
        print(f"❌ [Webhook Actions Logs] Error while fetching/extracting zip logs: {e}")
        return f"Error retrieving logs: {str(e)}"

async def handle_ci_workflow_failure(repo_name: str, run_id: int, workflow_name: str, installation_id: Optional[int], commit_sha: Optional[str] = None, branch: str = "main"):
    """Background task to fetch workflow logs and execute CI failure analysis."""
    cfg = get_settings()
    github_token = None
    
    if cfg.github_app_id and cfg.github_private_key and installation_id:
        try:
            from app.github_app import get_installation_access_token
            github_token = await get_installation_access_token(
                cfg.github_app_id, cfg.github_private_key, installation_id
            )
        except Exception as token_err:
            print(f"⚠️ [CI Webhook Log Loader] Failed to get dynamic installation token: {token_err}")
            
    if not github_token:
        github_token = cfg.github_token
        
    if not github_token:
        print("⚠️ [CI Webhook Log Loader] No credentials found. Cannot retrieve private logs.")
        logs = "Unavailable logs (No GitHub credentials configured to download Action logs)."
    else:
        logs = await fetch_github_workflow_logs(repo_name, run_id, github_token)
        
    await run_ci_pipeline_task(
        workflow_id=f"wf-{run_id}",
        repo_name=repo_name,
        failed_step=workflow_name,
        raw_logs=logs,
        installation_id=installation_id,
        commit_sha=commit_sha,
        branch=branch
    )

@router.post("/webhook")
async def github_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_hub_signature_256: Optional[str] = Header(None),
    x_github_event: Optional[str] = Header(None)
):
    """
    Unified GitHub Webhook receiver. Handles:
    1. 'pull_request' events (runs the LangGraph code review pipeline)
    2. 'workflow_run' events (fetches failed logs & runs the CI/CD self-healing agent)
    """
    body = await request.body()
    cfg = get_settings()
    
    print("\n" + "="*80)
    print(f"📥 [Webhook Received] Event: '{x_github_event}'")
    
    # Verify HMAC signature
    if not verify_signature(body, x_hub_signature_256 or "", cfg.github_webhook_secret):
        print("❌ [Webhook Signature Verification Failed] Unauthorized request rejected.")
        raise HTTPException(status_code=401, detail="Invalid webhook signature")
    print("✅ [Webhook Signature Verification Succeeded] Source authenticated.")
    
    try:
        payload = json.loads(body)
    except Exception:
        print("❌ [Webhook Error] Failed to parse payload JSON.")
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
        
    installation_id = payload.get("installation", {}).get("id")
    repo_name = payload.get("repository", {}).get("full_name", "unknown/repo")
    
    # --- 1. Handle GitHub Actions Workflow Run Failures ---
    if x_github_event == "workflow_run":
        action = payload.get("action")
        workflow_run = payload.get("workflow_run", {})
        conclusion = workflow_run.get("conclusion")
        
        if action == "completed" and conclusion == "failure":
            run_id = workflow_run.get("id")
            workflow_name = workflow_run.get("name", "Unknown Workflow")
            head_sha = workflow_run.get("head_sha")
            branch = workflow_run.get("head_branch", "main")
            print(f"🚨 [Webhook Event] Workflow run failed! ID: {run_id} | Name: '{workflow_name}' | Repo: {repo_name} | Commit SHA: {head_sha} | Branch: {branch}")
            
            background_tasks.add_task(
                handle_ci_workflow_failure,
                repo_name,
                run_id,
                workflow_name,
                installation_id,
                head_sha,
                branch
            )
            return {"status": "accepted", "event": "workflow_run_failure", "run_id": run_id}
            
        print(f"ℹ️ [Webhook Ignored] workflow_run action: '{action}', conclusion: '{conclusion}'")
        return {"status": "ignored", "reason": "Workflow was not completed with failure status."}

    # --- 2. Handle GitHub Issues ---
    if x_github_event == "issues":
        action = payload.get("action")
        issue = payload.get("issue", {})
        
        if action in ["opened", "reopened"]:
            issue_number = issue.get("number")
            issue_title = issue.get("title", f"Issue #{issue_number}")
            issue_body = issue.get("body", "")
            author = issue.get("user", {}).get("login", "unknown-author")
            issue_id = f"issue-{repo_name.replace('/', '-')}-{issue_number}"
            
            print(f"📬 [Webhook Event] Processing GitHub Issue #{issue_number}: '{issue_title}'")
            print(f"👤 Author: @{author} | Repo: {repo_name} | Action: {action}")
            
            background_tasks.add_task(
                run_issues_pipeline_task,
                issue_id,
                issue_number,
                issue_title,
                issue_body,
                repo_name,
                author,
                installation_id
            )
            return {"status": "accepted", "event": "issue_analysis", "issue_id": issue_id}
            
        print(f"ℹ️ [Webhook Ignored] Issues action '{action}' is not opened or reopened.")
        return {"status": "ignored", "reason": f"Issues action '{action}' ignored."}

    # --- 3. Handle Pull Request Code Reviews ---
    if x_github_event == "pull_request" or not x_github_event:
        action = payload.get("action")
        pull_request = payload.get("pull_request")
        
        if not pull_request or action not in ["opened", "reopened", "synchronize"]:
            print(f"ℹ️ [Webhook Ignored] Pull Request action '{action}' is not opened, reopened, or synchronize.")
            return {"status": "ignored", "reason": f"Event action '{action}' ignored."}
            
        pr_number = pull_request.get("number")
        pr_title = pull_request.get("title", f"Pull Request #{pr_number}")
        author = pull_request.get("user", {}).get("login", "unknown-author")
        pr_id = f"pr-{repo_name.replace('/', '-')}-{pr_number}"
        
        print(f"📬 [Webhook Event] Processing Pull Request #{pr_number}: '{pr_title}'")
        print(f"👤 Author: @{author} | Repo: {repo_name} | Action: {action}")
        
        # Fetch the diff
        api_diff_url = f"https://api.github.com/repos/{repo_name}/pulls/{pr_number}"
        diff_content = "Unavailable diff details (GitHub API credentials or connection not active)"
        
        if api_diff_url:
            print(f"🔗 [Webhook] Fetching diff via REST API from: {api_diff_url}")
            try:
                async with httpx.AsyncClient() as client:
                    headers = {}
                    github_token = None
                    
                    if cfg.github_app_id and cfg.github_private_key and installation_id:
                        try:
                            from app.github_app import get_installation_access_token
                            github_token = await get_installation_access_token(
                                cfg.github_app_id, cfg.github_private_key, installation_id
                            )
                        except Exception as token_err:
                            print(f"⚠️ [Webhook] Failed to generate token: {token_err}")
                            
                    if not github_token:
                        github_token = cfg.github_token
                        
                    if github_token:
                        headers["Authorization"] = f"Bearer {github_token}"
                        
                    headers["Accept"] = "application/vnd.github.v3.diff"
                    headers["User-Agent"] = "OpenReviewer-App"
                    
                    res = await client.get(api_diff_url, headers=headers, timeout=10.0, follow_redirects=True)
                    if res.status_code == 200:
                        diff_content = res.text
                        print(f"📄 [Webhook] Successfully downloaded code diff ({len(diff_content)} characters).")
                    else:
                        print(f"❌ [Webhook Error] GitHub REST API returned {res.status_code} for diff.")
            except Exception as e:
                print(f"❌ [Webhook Error] Exception downloading diff: {e}")
                
        print(f"🚀 [Webhook] Queueing review background task for PR ID: {pr_id}")
        background_tasks.add_task(
            run_pipeline_task,
            pr_id,
            pr_title,
            repo_name,
            author,
            diff_content,
            installation_id
        )
        return {"status": "accepted", "pr_id": pr_id}
        
    return {"status": "ignored", "reason": f"Unsupported event type '{x_github_event}'"}
