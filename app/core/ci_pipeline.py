import re
import base64
from typing import Dict, Any, Optional
import httpx

from app.db import save_ci_failure
from app.core.token_optimizer import get_repo_scoped_memory
from app.agents.ci_analyzer import analyze_ci_failure_node
from app.config import get_settings

def preprocess_ci_logs(raw_logs: str) -> dict:
    """
    Log Preprocessor. Scans raw logs, discards setup/install noise, 
    and extracts only the exact error lines and stacktrace (max 3000 chars)
    to enforce token optimization.
    """
    if not raw_logs:
        return {
            "error_summary": "Empty log trace received.",
            "stacktrace": "No log output."
        }
        
    lines = raw_logs.splitlines()
    error_lines = []
    stacktrace_lines = []
    
    # 1. Look for typical error and traceback tags
    error_patterns = [
        r"(?i)(error|exception|fail|failed|critical):",
        r"(?i)module_not_found_error|modulenotfounderror",
        r"(?i)syntaxerror|indentationerror|assertionerror",
        r"(?i)failed in \d+s|exit code \d+"
    ]
    
    # Track the first line where the error or stacktrace starts
    error_start_idx = -1
    for idx, line in enumerate(lines):
        if any(re.search(pat, line) for pat in error_patterns) or "traceback" in line.lower():
            error_start_idx = idx
            break
            
    # 2. Extract context window (last 20 lines before error, and 50 lines after)
    if error_start_idx != -1:
        start = max(0, error_start_idx - 15)
        end = min(len(lines), error_start_idx + 60)
        
        # Isolate the main error line as a summary
        error_summary = lines[error_start_idx].strip()
        
        # Isolate the stacktrace context
        stacktrace_lines = lines[start:end]
    else:
        # Fallback: if no clear error keyword found, grab the last 60 lines of the build log
        error_summary = "Unrecognized pipeline crash signature."
        stacktrace_lines = lines[-60:]
        
    stacktrace = "\n".join(stacktrace_lines)
    
    # Enforce token budget limits (max 3000 characters for stacktrace context)
    max_chars = 3000
    if len(stacktrace) > max_chars:
        trunc_msg = "\n... [TRUNCATED LOGS BY PREPROCESSOR] ..."
        stacktrace = stacktrace[:max_chars - len(trunc_msg)] + trunc_msg
        
    return {
        "error_summary": error_summary,
        "stacktrace": stacktrace
    }

async def auto_heal_github_code(repo: str, file_path: str, new_content: str, token: str, branch: str = "main") -> bool:
    """
    Self-Healing Engine. Automatically updates repository files on GitHub 
    to fix code errors, triggering successful CI re-runs autonomously.
    """
    print(f"⚙️  [Self-Healing] Resolving GitHub state for: {file_path} in {repo} on branch {branch}")
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "AI-Self-Healing-Agent"
    }
    
    try:
        # 1. Fetch file meta to get its active Git SHA
        content_url = f"https://api.github.com/repos/{repo}/contents/{file_path}?ref={branch}"
        async with httpx.AsyncClient() as client:
            res = await client.get(content_url, headers=headers, timeout=5.0)
            if res.status_code != 200:
                print(f"⚠️  [Self-Healing Failed] Could not find file {file_path} in GitHub on branch {branch}.")
                return False
            
            file_meta = res.json()
            current_sha = file_meta["sha"]
            
        # 2. Base64 encode the corrected content
        encoded_content = base64.b64encode(new_content.encode("utf-8")).decode("utf-8")
        
        # 3. PUT the update directly back to GitHub (commits dynamically)
        payload = {
            "message": f"fix(ci): automatically heal build failure in {file_path}",
            "content": encoded_content,
            "sha": current_sha,
            "branch": branch
        }
        
        async with httpx.AsyncClient() as client:
            put_res = await client.put(content_url, headers=headers, json=payload, timeout=10.0)
            if put_res.status_code in [200, 201]:
                print(f"🎉 [Self-Healing Success] Automatically pushed code fix for {file_path} back to main branch!")
                return True
            else:
                print(f"⚠️  [Self-Healing Failed] GitHub contents update returned {put_res.status_code}: {put_res.text}")
                return False
                
    except Exception as e:
        print(f"⚠️  [Self-Healing Error] Git push connection failed: {e}")
        return False

def extract_code_and_path(report: str, raw_logs: str) -> tuple[Optional[str], Optional[str]]:
    """
    Robustly extracts the code fix and the target file path from the AI report.
    Supports carriage returns, different language tags, and loose spacing.
    """
    # 1. Try matching triple backtick code blocks with loose matching
    code_blocks = re.findall(r"```[a-zA-Z]*[\r\n]+(.*?)(?:[\r\n]+)?```", report, re.DOTALL)
    
    if not code_blocks:
        code_blocks = re.findall(r"```(?:python|javascript|json)?\s*(.*?)\s*```", report, re.DOTALL)
        
    corrected_code = None
    if code_blocks:
        for block in code_blocks:
            clean_block = block.strip()
            if any(kw in clean_block for kw in ["def ", "import ", "assert ", "class ", "const ", "let ", "function"]):
                corrected_code = clean_block
                break
        if not corrected_code:
            corrected_code = code_blocks[0].strip()

    # 2. Extract file path
    file_path = None
    file_match = re.search(r"(?:file|path|target|at|in)\s+([a-zA-Z0-9_\-/]+\.(?:py|js|json))", report, re.IGNORECASE)
    if not file_match:
        file_match = re.search(r"([a-zA-Z0-9_\-/]+\.(?:py|js|json))", report)
        
    if file_match:
        file_path = file_match.group(1).strip()
        # Clean up common markdown trailing characters
        file_path = file_path.rstrip(".:*` ")
        
        # Robust path resolution: check if logs contain a folder prefix for this file
        if "/" not in file_path:
            path_in_logs = re.search(r"([a-zA-Z0-9_\-/]+/" + re.escape(file_path) + r")", raw_logs)
            if path_in_logs:
                resolved_path = path_in_logs.group(1).strip()
                print(f"[CI Path Resolver] Resolved '{file_path}' to '{resolved_path}'")
                file_path = resolved_path

    return corrected_code, file_path

async def run_ci_pipeline_task(
    workflow_id: str,
    repo_name: str,
    failed_step: str,
    raw_logs: str,
    installation_id: Optional[int] = None,
    commit_sha: Optional[str] = None,
    branch: str = "main"
):
    """Runs the token-optimized CI/CD failure analysis pipeline."""
    print(f"\n⚙️  [CI Pipeline] Starting analysis for workflow: {workflow_id} in {repo_name}")
    
    # 1. Initial running status in DB
    save_ci_failure(workflow_id, {
        "workflow_id": workflow_id,
        "repo_name": repo_name,
        "failed_step": failed_step,
        "raw_logs": raw_logs,
        "status": "running",
        "error_summary": "Analyzing logs...",
        "stacktrace": "Preprocessing raw logs...",
        "report": "Scanning logs to identify root cause and draft remediation fixes...",
        "domain": "unknown",  # 'code-side' or 'deployment-side'
        "installation_id": installation_id
    })
    
    try:
        # 2. Log Preprocessing (saves 98% tokens)
        print("[CI Pipeline] Preprocessing raw logs and filtering noise...")
        log_meta = preprocess_ci_logs(raw_logs)
        error_summary = log_meta["error_summary"]
        stacktrace = log_meta["stacktrace"]
        
        # 3. Retrieve repo-scoped memory
        print(f"[CI Pipeline] Loading repo-scoped memory for {repo_name}...")
        repo_context = get_repo_scoped_memory(repo_name)
        
        # 4. LLM Analysis
        print("[CI Pipeline] Analyzing failure using Groq LLM...")
        report = await analyze_ci_failure_node(
            repo_name=repo_name,
            workflow_id=workflow_id,
            failed_step=failed_step,
            error_summary=error_summary,
            stacktrace=stacktrace,
            repo_context=repo_context
        )
        
        # 5. Classify Domain (Code-side vs Deployment-side)
        domain = "code-side"
        # Naive keyword parser to detect domain
        lower_report = report.lower()
        if "deployment-side" in lower_report or "infrastructure" in lower_report or "aws" in lower_report or "gcp" in lower_report or "docker pull" in lower_report or "iam" in lower_report:
            domain = "deployment-side"
            
        print(f"[CI Pipeline] Failure classified as: {domain.upper()}")
        
        # 6. Publish feedback
        cfg = get_settings()
        github_token = None
        
        if cfg.github_app_id and cfg.github_private_key and installation_id:
            try:
                from app.github_app import get_installation_access_token
                github_token = await get_installation_access_token(
                    cfg.github_app_id, cfg.github_private_key, installation_id
                )
            except Exception as e:
                print(f"[CI Pipeline] Failed to generate dynamic token: {e}")
                
        if not github_token:
            github_token = cfg.github_token
            
        # Post to GitHub depending on domain
        target_sha = commit_sha or workflow_id
        if github_token and repo_name:
            if domain == "code-side":
                # If there's an active PR associated, post a comment (simulate/post)
                print(f"[CI Pipeline] Posting PR review comment for Code-Side failure...")
                # We can also post a status check (Red Cross ❌)
                await post_github_check(repo_name, target_sha, "failure", "CI/CD failure detected: Code-side bug.", github_token)
                
                # 7. Self-Healing Commit Push back to GitHub
                print("[CI Pipeline] Running Self-Healing Engine...")
                corrected_code, file_path = extract_code_and_path(report, raw_logs)
                
                if corrected_code and file_path:
                    print(f"[CI Pipeline] Extracted self-healing fix for: {file_path}")
                    await auto_heal_github_code(repo_name, file_path, corrected_code, github_token, branch)
                else:
                    print(f"[CI Pipeline] Self-Healing skipped: corrected_code={bool(corrected_code)}, file_path={file_path}")
            else:
                # Deployment-side: Post an alert Issue
                print(f"[CI Pipeline] Creating GitHub Issue for Deployment-Side / Infra failure...")
                await create_github_issue(repo_name, failed_step, report, github_token)
                await post_github_check(repo_name, target_sha, "error", "CI/CD failure detected: Cloud/Infra issue.", github_token)
        else:
            print("[CI Pipeline] Skipping real GitHub posting (running in local simulation mode).")
            
        # 8. Save final status in DB
        save_ci_failure(workflow_id, {
            "workflow_id": workflow_id,
            "repo_name": repo_name,
            "failed_step": failed_step,
            "raw_logs": raw_logs,
            "status": "completed",
            "error_summary": error_summary,
            "stacktrace": stacktrace,
            "report": report,
            "domain": domain,
            "installation_id": installation_id
        })
        print(f"🎉 [CI Pipeline Success] Log analysis completed for {workflow_id}.\n")
        
    except Exception as e:
        print(f"❌ [CI Pipeline Error] Failed log analysis: {e}")
        save_ci_failure(workflow_id, {
            "workflow_id": workflow_id,
            "repo_name": repo_name,
            "failed_step": failed_step,
            "raw_logs": raw_logs,
            "status": "failed",
            "error_summary": "Pipeline execution failed.",
            "stacktrace": str(e),
            "report": f"Analysis crashed: {e}",
            "domain": "unknown"
        })

async def post_github_check(repo: str, commit_sha: str, state: str, description: str, token: str):
    """Utility to post status checks directly to the GitHub commit."""
    if not commit_sha.startswith("wf-"):
        # Real commit checks need real SHAs
        try:
            url = f"https://api.github.com/repos/{repo}/statuses/{commit_sha}"
            headers = {
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "AI-Agent-Orchestrator"
            }
            payload = {
                "state": state,
                "description": description[:139],
                "context": "AI CI-Failure Analyzer"
            }
            async with httpx.AsyncClient() as client:
                await client.post(url, headers=headers, json=payload, timeout=5.0)
        except Exception as e:
            print(f"[CI Pipeline] Github Status API post failed: {e}")

async def create_github_issue(repo: str, failed_step: str, body: str, token: str):
    """Utility to create a new GitHub Issue for infrastructure failures."""
    try:
        url = f"https://api.github.com/repos/{repo}/issues"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "AI-Agent-Orchestrator"
        }
        payload = {
            "title": f"⚠️ CI/CD Infrastructure Failure Alert in step: '{failed_step}'",
            "body": f"This issue was generated automatically by the AI CI-Failure Analyzer.\n\n{body}",
            "labels": ["devops", "ci-failure", "infrastructure"]
        }
        async with httpx.AsyncClient() as client:
            res = await client.post(url, headers=headers, json=payload, timeout=8.0)
            if res.status_code == 201:
                print(f"[CI Pipeline] Created GitHub Alert Issue successfully.")
            else:
                print(f"[CI Pipeline Failed] GitHub Issues API returned {res.status_code}: {res.text}")
    except Exception as e:
        print(f"[CI Pipeline Failed] Failed to create GitHub issue: {e}")
