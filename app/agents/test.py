import json
from app.llm import call_llm

async def test_agent_node(state: dict) -> dict:
    """Suggests test cases and highlights missing coverage."""
    print("[Test Agent] Checking test coverage and drafting test templates (Token Optimized)...")
    
    # Extract static test findings
    findings = state.get("static_findings", {}).get("test", [])
    findings_str = json.dumps(findings, indent=2) if findings else "No testing or coverage gaps pre-flagged by static analysis."
    
    system_prompt = (
        "You are a Senior QA and Testing Agent. Your goal is to review code diffs and identify missing "
        "test coverage for new logic, edge cases that require tests, and provide concrete unit tests.\n\n"
        "To save token costs, you are provided with:\n"
        "1. Repo-scoped test suite guidelines & frameworks.\n"
        "2. Deterministic new functions lacking tests pre-checked findings.\n"
        "3. A token-optimized and condensed code diff.\n\n"
        "Your task:\n"
        "- Explain the coverage gaps identified by the pre-checked findings.\n"
        "- Draft a robust, ready-to-copy unit test template using `pytest` (or relevant framework based on file language).\n\n"
        "Formatting Rules:\n"
        "1. Do NOT use bullet points for findings that contain code blocks. Bullet points cause markdown nesting and indentation bugs.\n"
        "2. Format your test cases and coverage gaps with standard Markdown headings, e.g.:\n"
        "### 🧪 Missing Coverage / Boilerplate Tests\n"
        "3. Always ensure your Python code blocks are opened and closed correctly using standard triple backticks: ```python and ```."
    )
    
    user_prompt = (
        f"PR Title: {state['pr_title']}\n"
        f"Repository: {state['repo_name']}\n\n"
        f"--- Scoped Repo Memory ---\n{state.get('repo_context', 'None')}\n\n"
        f"--- Pre-Checked Static Findings ---\n{findings_str}\n\n"
        f"--- Optimized Diff Content ---\n{state.get('optimized_diff', '')}"
    )
    
    report = await call_llm(system_prompt, user_prompt)
    return {"test_report": report}
