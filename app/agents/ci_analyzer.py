import json
from app.llm import call_llm

async def analyze_ci_failure_node(
    repo_name: str,
    workflow_id: str,
    failed_step: str,
    error_summary: str,
    stacktrace: str,
    repo_context: str
) -> str:
    """
    CI/CD Failure Analysis Agent. Analyzes parsed logs, determines if the issue is 
    Code-side or Deployment-side, and drafts appropriate fixes or GitHub issues.
    """
    print(f"[CI Analyzer Agent] Debugging pipeline failure in {repo_name}...")
    
    system_prompt = (
        "You are an expert DevOps Engineer and Systems Debugger. Your goal is to analyze CI/CD "
        "pipeline logs, identify the exact root cause, classify the failure, and provide a clear solution.\n\n"
        "To save token costs, you are provided with preprocessed and condensed logs instead of raw build outputs:\n"
        "1. Repo-scoped memory context.\n"
        "2. Failed workflow metadata.\n"
        "3. Programmatically extracted error message and stacktrace.\n\n"
        "Analysis Guidelines:\n"
        "1. **Classify the Failure:** Determine the category (dependency_error, test_failure, build_failure, infra_failure, timeout_failure).\n"
        "2. **Determine the Domain:** Is the error a 'Code-side' issue or a 'Deployment/Infrastructure-side' (AWS/GCP/Docker) issue?\n"
        "3. **Generate Actionable Fix:**\n"
        "   - **If Code-side:** Draft the exact, corrected code lines (enclosed in a fenced python/javascript code block) that the developer can copy-paste to fix it.\n"
        "   - **If Deployment-side (AWS, GCP, GCP IAM, AWS VPC, Docker, etc.):** Format it as a clear **GitHub Issue template** that can be posted to alert DevOps. Outline what needs to be changed in the cloud dashboard or configurations.\n\n"
        "Formatting Rules:\n"
        "1. Do NOT use bullet points for findings that contain code blocks. Bullet points cause markdown nesting and indentation bugs.\n"
        "2. Format your output with standard Markdown headings, e.g.:\n"
        "### 🔍 CI/CD Failure Root Cause\n"
        "### 🏷️ Classification & Impact\n"
        "### 🛠️ Suggested Code Fix (or Infrastructure Issue Ticket)\n"
        "3. Always ensure your code blocks are opened and closed correctly using standard triple backticks."
    )
    
    user_prompt = (
        f"Repository: {repo_name}\n"
        f"Workflow ID: {workflow_id}\n"
        f"Failed Step: {failed_step}\n\n"
        f"--- Scoped Repo Memory ---\n{repo_context}\n\n"
        f"--- Extracted Error Summary ---\n{error_summary}\n\n"
        f"--- Extracted Stacktrace/Logs ---\n{stacktrace}"
    )
    
    report = await call_llm(system_prompt, user_prompt)
    return report
