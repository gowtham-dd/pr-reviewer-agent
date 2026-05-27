import re
import base64
from typing import Dict, Any, Optional
import httpx

from app.db import save_issue
from app.config import get_settings
from app.llm import call_llm

def extract_file_paths(text: str) -> list[str]:
    """
    Scans the issue text (title and body) for potential file paths in the repo.
    Matches paths ending in common extensions like .py, .js, .json, .ts, .html, .css, etc.
    """
    if not text:
        return []
    # Match strings resembling file paths or filenames
    pattern = r"\b([a-zA-Z0-9_\-/]+\.(?:py|js|json|ts|html|css|sh|md|yml|yaml|txt))\b"
    matches = re.findall(pattern, text)
    # Remove duplicates and filter out noise
    unique_matches = list(set(matches))
    return [path for path in unique_matches if not path.endswith(("issues.json", "reviews.json", "ci_failures.json"))]

async def fetch_github_file_content(repo: str, file_path: str, token: str, branch: str = "main") -> Optional[str]:
    """
    Downloads file content from a repository on GitHub.
    """
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "OpenReviewer-Issues-Agent"
    }
    url = f"https://api.github.com/repos/{repo}/contents/{file_path}?ref={branch}"
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(url, headers=headers, timeout=10.0)
            if res.status_code == 200:
                meta = res.json()
                content_encoded = meta.get("content", "")
                if content_encoded:
                    return base64.b64decode(content_encoded).decode("utf-8", errors="ignore")
            print(f"⚠️ [Issues Path Loader] GitHub contents API returned status {res.status_code} for {file_path}")
            return None
    except Exception as e:
        print(f"❌ [Issues Path Loader] Exception loading file {file_path}: {e}")
        return None

async def post_issue_comment(repo: str, issue_number: int, body: str, token: str):
    """
    Posts a diagnostic/remediation comment back to the GitHub Issue.
    """
    url = f"https://api.github.com/repos/{repo}/issues/{issue_number}/comments"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "OpenReviewer-Issues-Agent"
    }
    payload = {"body": body}
    try:
        async with httpx.AsyncClient() as client:
            res = await client.post(url, headers=headers, json=payload, timeout=10.0)
            if res.status_code == 201:
                print(f"🎉 [Issues API] Posted comment successfully to Issue #{issue_number}")
            else:
                print(f"❌ [Issues API] Failed to post comment. Status {res.status_code}: {res.text}")
    except Exception as e:
        print(f"❌ [Issues API] Exception posting comment to Issue #{issue_number}: {e}")

async def run_issues_pipeline_task(
    issue_id: str,
    issue_number: int,
    issue_title: str,
    issue_body: str,
    repo_name: str,
    author: str,
    installation_id: Optional[int] = None,
    branch: str = "main"
):
    """
    Background worker that runs the Issues analysis pipeline.
    """
    print(f"\n🏷️ [Issues Pipeline] Analyzing Issue #{issue_number}: '{issue_title}' in {repo_name}")
    
    # 1. Initialize running state
    save_issue(issue_id, {
        "issue_id": issue_id,
        "issue_number": issue_number,
        "issue_title": issue_title,
        "issue_body": issue_body or "",
        "repo_name": repo_name,
        "author": author,
        "status": "running",
        "criticality": "unknown",
        "target_file": "scanning...",
        "file_content": "",
        "report": "Scanning issue and analyzing repository files..."
    })

    # Get GitHub authentication token
    cfg = get_settings()
    github_token = None
    if cfg.github_app_id and cfg.github_private_key and installation_id:
        try:
            from app.github_app import get_installation_access_token
            github_token = await get_installation_access_token(
                cfg.github_app_id, cfg.github_private_key, installation_id
            )
        except Exception as e:
            print(f"⚠️ [Issues Pipeline] Failed to generate installation token: {e}")

    if not github_token:
        github_token = cfg.github_token

    try:
        # 2. Extract referenced files from title and body
        combined_text = f"{issue_title}\n{issue_body or ''}"
        found_files = extract_file_paths(combined_text)
        
        target_file = "None"
        file_content = ""
        
        if found_files and github_token:
            # We take the first matched file path
            candidate_file = found_files[0]
            print(f"🔍 [Issues Pipeline] Found file path candidate: {candidate_file}")
            fetched_content = await fetch_github_file_content(repo_name, candidate_file, github_token, branch)
            if fetched_content is not None:
                target_file = candidate_file
                file_content = fetched_content
                print(f"✅ [Issues Pipeline] Successfully retrieved file content for {target_file} ({len(file_content)} chars)")
            else:
                # If path isn't relative to root, we list it but keep empty content
                target_file = f"{candidate_file} (Not found in repo root)"
        
        # 3. Call LLM to classify and write remediation report
        print("[Issues Pipeline] Dispatching to LLM for Diagnostic & Remedy Planning...")
        
        system_prompt = (
            "You are an expert DevOps and Software Engineering Agent.\n"
            "Your task is to analyze a GitHub Issue report, classify its criticality, and provide a remedy.\n\n"
            "Classification Rules:\n"
            "- CRITICAL: Security vulnerabilities, credentials exposure, major application crashes (e.g. SegFault, unhandled 500 exceptions in core workflows), data corruption, or severe performance degradation making the service unusable.\n"
            "- NON-CRITICAL: Styling updates, minor bugs, typos, refactoring, new feature requests, test coverage enhancements, documentation updates, or warnings.\n\n"
            "Please output your analysis in standard markdown format, focusing on:\n"
            "1. **Criticality Classification**: State if it is CRITICAL or NON-CRITICAL and explain why.\n"
            "2. **Issue Diagnosis**: Detailed explanation of what the issue means, what causes it, and what needs fixing.\n"
            "3. **Remedy / Action Plan**: Step-by-step instructions or direct code corrections (enclosed in ```code blocks) to fully resolve the issue.\n\n"
            "Keep the output extremely helpful, professional, and clear."
        )
        
        user_prompt = (
            f"Repository: {repo_name}\n"
            f"Issue Title: {issue_title}\n"
            f"Issue Author: @{author}\n"
            f"Issue Body:\n{issue_body or 'No body provided.'}\n\n"
        )
        if file_content:
            user_prompt += (
                f"Target File: {target_file}\n"
                f"Active File Content:\n"
                f"```\n"
                f"{file_content[:5000]}\n"
                f"```\n"
            )
        else:
            user_prompt += "No active source file was detected or found in the repository root for this issue.\n"

        # Invoke LLM
        report = await call_llm(system_prompt, user_prompt)
        
        # Parse criticality from report
        criticality = "non-critical"
        if "criticality: critical" in report.lower() or "**criticality**: critical" in report.lower() or "is critical" in report.lower():
            criticality = "critical"
        elif "criticality: non-critical" in report.lower() or "**criticality**: non-critical" in report.lower():
            criticality = "non-critical"
        
        print(f"📊 [Issues Pipeline] Classified Criticality: {criticality.upper()}")

        # 4. Post comment to GitHub if authenticated
        if github_token:
            comment_body = (
                f"### 🤖 AI Issue Diagnostic & Remedy Report\n\n"
                f"**Criticality Assessment:** {criticality.upper()}\n\n"
                f"{report}\n\n"
                f"--- \n"
                f"*Comment posted automatically by the OpenReviewer AI Platform.*"
            )
            await post_issue_comment(repo_name, issue_number, comment_body, github_token)
        else:
            print("⚠️ [Issues Pipeline] Skipping GitHub Comment (No authentication token available)")

        # 5. Save completed state in DB
        save_issue(issue_id, {
            "issue_id": issue_id,
            "issue_number": issue_number,
            "issue_title": issue_title,
            "issue_body": issue_body or "",
            "repo_name": repo_name,
            "author": author,
            "status": "completed",
            "criticality": criticality,
            "target_file": target_file,
            "file_content": file_content,
            "report": report
        })
        print(f"🎉 [Issues Pipeline Success] Log analysis completed for Issue #{issue_number}.\n")

    except Exception as e:
        print(f"❌ [Issues Pipeline Error] Failed to complete analysis: {e}")
        save_issue(issue_id, {
            "issue_id": issue_id,
            "issue_number": issue_number,
            "issue_title": issue_title,
            "issue_body": issue_body or "",
            "repo_name": repo_name,
            "author": author,
            "status": "failed",
            "criticality": "unknown",
            "target_file": "failed",
            "file_content": "",
            "report": f"Pipeline analysis crashed: {e}"
        })
