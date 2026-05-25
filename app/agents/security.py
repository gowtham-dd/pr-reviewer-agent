import json
from app.llm import call_llm

async def security_agent_node(state: dict) -> dict:
    """Runs security analysis on the code diff using preprocessed static findings and optimized diff."""
    print("[Security Agent] Analyzing vulnerabilities (Token Optimized)...")
    
    # Extract static findings
    findings = state.get("static_findings", {}).get("security", [])
    findings_str = json.dumps(findings, indent=2) if findings else "No critical patterns pre-flagged by static analysis."
    
    system_prompt = (
        "You are an expert Security Code Reviewer specialized in OWASP Top 10, secret detection, "
        "and injection risks. Your goal is to review code diffs and explain/verify security concerns.\n\n"
        "To save token costs, you are provided with:\n"
        "1. Repo-scoped architectural rules.\n"
        "2. Deterministic linter/scanner pre-checked findings.\n"
        "3. A token-optimized and condensed code diff.\n\n"
        "Your task:\n"
        "- Verify and explain any pre-checked static findings.\n"
        "- Identify any additional critical security risks in the diff.\n"
        "- Suggest precise fixes using secure patterns (e.g. parameterized queries, environment variables).\n\n"
        "Formatting Rules:\n"
        "1. Do NOT use bullet points (e.g. *, -, or numbers) for findings that contain code blocks. Bullet points cause markdown nesting and indentation bugs.\n"
        "2. Format each finding with a standard Markdown heading, e.g.:\n"
        "### 🚨 [SEVERITY] Finding Title\n"
        "3. Provide the vulnerability description, recommendation, and a properly formatted, fenced code block.\n"
        "4. Always ensure code blocks are opened and closed correctly using standard triple backticks with a language specifier (e.g. ```python or ```javascript) and are NOT indented."
    )
    
    user_prompt = (
        f"PR Title: {state['pr_title']}\n"
        f"Repository: {state['repo_name']}\n\n"
        f"--- Scoped Repo Memory ---\n{state.get('repo_context', 'None')}\n\n"
        f"--- Pre-Checked Static Findings ---\n{findings_str}\n\n"
        f"--- Optimized Diff Content ---\n{state.get('optimized_diff', '')}"
    )
    
    report = await call_llm(system_prompt, user_prompt)
    return {"security_report": report}
