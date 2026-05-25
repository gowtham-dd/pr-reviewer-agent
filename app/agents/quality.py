import json
from app.llm import call_llm

async def quality_agent_node(state: dict) -> dict:
    """Runs code styling, formatting, and complexity checks."""
    print("[Code Quality Agent] Checking style and complexity (Token Optimized)...")
    
    # Extract static quality findings
    findings = state.get("static_findings", {}).get("quality", [])
    findings_str = json.dumps(findings, indent=2) if findings else "No code quality or complexity issues pre-flagged by static analysis."
    
    system_prompt = (
        "You are a specialized Code Quality, PEP-8, and Architecture Agent. Your goal is to review code diffs "
        "for style violations, cognitive complexity, magic numbers, poor naming, or refactoring opportunities.\n\n"
        "To save token costs, you are provided with:\n"
        "1. Repo-scoped styling rules & naming conventions.\n"
        "2. Deterministic code complexity and magic number pre-checked findings.\n"
        "3. A token-optimized and condensed code diff.\n\n"
        "Your task:\n"
        "- Verify and explain any pre-checked style/complexity issues.\n"
        "- Suggest optimizations for readibility, refactoring, and PEP-8/industry conventions.\n\n"
        "Formatting Rules:\n"
        "1. Do NOT use bullet points for findings that contain code blocks. Bullet points cause markdown nesting and indentation bugs.\n"
        "2. Format each finding with a standard Markdown heading, e.g.:\n"
        "### 🔧 [SEVERITY] Finding Title\n"
        "3. Provide descriptions and a properly formatted, fenced code block for suggestions.\n"
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
    return {"quality_report": report}
