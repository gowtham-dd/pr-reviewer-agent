import json
import httpx
from typing import Optional
from fastapi import APIRouter, Request, Header, HTTPException, BackgroundTasks

from app.config import get_settings
from app.webhook import verify_signature
from app.core.pipeline import run_pipeline_task

router = APIRouter(tags=["Webhooks"])

@router.post("/webhook")
async def github_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_hub_signature_256: Optional[str] = Header(None)
):
    """
    Standard GitHub Webhook endpoint. Validates HMAC signature,
    and runs the LangGraph review pipeline in a background thread.
    """
    body = await request.body()
    cfg = get_settings()
    
    print("\n" + "="*80)
    print(f"📥 [Webhook Received] Incoming request from GitHub!")
    
    # 1. Validate signature to protect against webhook spoofing
    print("🔒 [Webhook] Verifying HMAC SHA-256 signature...")
    if not verify_signature(body, x_hub_signature_256 or "", cfg.github_webhook_secret):
        print("❌ [Webhook Signature Verification Failed] Unauthorized request rejected.")
        raise HTTPException(status_code=401, detail="Invalid webhook signature")
    print("✅ [Webhook Signature Verification Succeeded] Source authenticated.")
    
    # 2. Parse event payload
    try:
        payload = json.loads(body)
    except Exception:
        print("❌ [Webhook Error] Failed to parse payload JSON.")
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
    
    # We only care about pull_request events (opened, reopened, or synchronized)
    action = payload.get("action")
    pull_request = payload.get("pull_request")
    
    if not pull_request or action not in ["opened", "reopened", "synchronize"]:
        print(f"ℹ️ [Webhook Ignored] Action '{action}' is not opened, reopened, or synchronize.")
        return {"status": "ignored", "reason": f"Event action '{action}' ignored."}

    pr_number = pull_request.get("number")
    repo_name = payload.get("repository", {}).get("full_name", "unknown/repo")
    pr_title = pull_request.get("title", f"Pull Request #{pr_number}")
    author = pull_request.get("user", {}).get("login", "unknown-author")
    pr_id = f"pr-{repo_name.replace('/', '-')}-{pr_number}"

    print(f"📬 [Webhook Event] Processing Pull Request #{pr_number}: '{pr_title}'")
    print(f"👤 Author: @{author} | Repo: {repo_name} | Action: {action}")

    # Extract installation ID for GitHub App auth
    installation_id = payload.get("installation", {}).get("id")
    print(f"🆔 GitHub App Installation ID: {installation_id}")

    # Fetch the code diff from GitHub REST API to ensure private repos can be accessed securely via authorization tokens
    api_diff_url = f"https://api.github.com/repos/{repo_name}/pulls/{pr_number}"
    diff_content = "Mocked diff details (GitHub API credentials or connection not active)"
    if api_diff_url:
        print(f"🔗 [Webhook] Fetching diff via REST API from: {api_diff_url}")
        try:
            async with httpx.AsyncClient() as client:
                headers = {}
                github_token = None
                
                # Try getting dynamic GitHub App token first
                if cfg.github_app_id and cfg.github_private_key and installation_id:
                    print("🔑 [Webhook] Exchanging GitHub App JWT for installation access token...")
                    try:
                        from app.github_app import get_installation_access_token
                        github_token = await get_installation_access_token(
                            cfg.github_app_id, cfg.github_private_key, installation_id
                        )
                        print("🔑 [Webhook] Successfully generated dynamic access token!")
                    except Exception as token_err:
                        print(f"⚠️ [Webhook] Failed to generate dynamic token: {token_err}. Trying fallback...")
                
                # Fallback to PAT
                if not github_token:
                    if cfg.github_token:
                        print("🔑 [Webhook] Falling back to standard GITHUB_TOKEN (Personal Access Token).")
                        github_token = cfg.github_token
                    else:
                        print("⚠️ [Webhook] No GITHUB_TOKEN or App credentials found. Running in unauthenticated mode.")
                    
                if github_token:
                    # Bearer token is standard and robust for GitHub installation tokens and modern PATs
                    headers["Authorization"] = f"Bearer {github_token}"
                
                headers["Accept"] = "application/vnd.github.v3.diff"
                headers["User-Agent"] = "OpenReviewer-App"
                
                res = await client.get(api_diff_url, headers=headers, timeout=10.0, follow_redirects=True)
                if res.status_code == 200:
                    diff_content = res.text
                    print(f"📄 [Webhook] Successfully downloaded code diff ({len(diff_content)} characters).")
                else:
                    print(f"❌ [Webhook Error] GitHub REST API returned status code {res.status_code} while pulling diff: {res.text}")
        except Exception as e:
            print(f"❌ [Webhook Error] Exception occurred when downloading diff: {e}")

    print(f"🚀 [Webhook] Queueing pipeline background task for PR ID: {pr_id}")
    print("="*80 + "\n")
    
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
