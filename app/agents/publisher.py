import httpx
from app.config import get_settings

async def publish_report_node(state: dict) -> dict:
    """Executes after approval. Posts to GitHub API and triggers Teams Webhooks."""
    print(f"[Publisher] Publishing review findings. Decision: {state['decision']}")
    cfg = get_settings()
    
    if state["decision"] == "approved":
        # Post to Teams if configured
        if cfg.teams_webhook_url:
            print("[Publisher] Posting notification to MS Teams workflow...")
            try:
                # Microsoft Teams Adaptive Card format
                card = {
                    "type": "message",
                    "attachments": [{
                        "contentType": "application/vnd.microsoft.card.adaptive",
                        "content": {
                            "type": "AdaptiveCard",
                            "body": [
                                {
                                    "type": "TextBlock",
                                    "size": "Medium",
                                    "weight": "Bolder",
                                    "text": f"✅ PR Approved for Publishing: {state['pr_title']}"
                                },
                                {
                                    "type": "TextBlock",
                                    "text": f"**Repository**: {state['repo_name']}\n**Author**: {state['author']}"
                                },
                                {
                                    "type": "TextBlock",
                                    "text": f"**Comments**: {state.get('feedback', 'No feedback provided.')}",
                                    "isSubtle": True
                                }
                            ],
                            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                            "version": "1.4"
                        }
                    }]
                }
                async with httpx.AsyncClient() as client:
                    await client.post(cfg.teams_webhook_url, json=card, timeout=5.0)
            except Exception as e:
                print(f"[Publisher] Teams webhook post failed: {e}")
        
        # Determine token for posting comments
        github_token = None
        installation_id = state.get("installation_id")
        
        if cfg.github_app_id and cfg.github_private_key and installation_id:
            try:
                from app.github_app import get_installation_access_token
                github_token = await get_installation_access_token(
                    cfg.github_app_id, cfg.github_private_key, installation_id
                )
                print(f"[Publisher] Successfully generated dynamic installation token for posting review.")
            except Exception as token_err:
                print(f"[Publisher] Failed to generate dynamic installation token: {token_err}")
        
        # Fallback to Personal Access Token
        if not github_token:
            github_token = cfg.github_token
 
        # Post to GitHub PR Comments if Token is provided and it's a real PR
        if github_token and state["pr_id"].startswith("pr-"):
            print("[Publisher] Posting consolidated report back to GitHub PR comments...")
            try:
                # Extract PR number from the trailing part of pr_id (e.g. pr-owner-repo-12 -> 12)
                pr_number = state["pr_id"].split("-")[-1]
                repo = state["repo_name"]
                
                url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/reviews"
                headers = {
                    "Authorization": f"token {github_token}",
                    "Accept": "application/vnd.github.v3+json",
                    "User-Agent": "OpenReviewer-App"
                }
                
                # Append human feedback to the consolidated report
                human_feedback = state.get("feedback", "")
                publish_body = state["consolidated_report"]
                if human_feedback:
                    publish_body += f"\n\n---\n\n### ✍️ Human Gate Reviewer Feedback:\n> {human_feedback}"
                
                payload = {
                    "body": publish_body,
                    "event": "COMMENT"
                }
                
                async with httpx.AsyncClient() as client:
                    res = await client.post(url, headers=headers, json=payload, timeout=8.0)
                    if res.status_code in [200, 201]:
                        print(f"[Publisher] Successfully posted consolidated review on GitHub PR #{pr_number}")
                    else:
                        print(f"[Publisher Failed] GitHub returned {res.status_code}: {res.text}")
            except Exception as e:
                print(f"[Publisher Failed] Exception during GitHub API request: {e}")
        else:
            print("[Publisher] Skipping real GitHub PR posting (running in local simulation mode or GITHUB_TOKEN/installation_token not configured).")
            
        return {"status": "completed"}
    else:
        print("[Publisher] PR review was rejected by human gate moderator. Review findings not posted.")
        return {"status": "rejected"}
