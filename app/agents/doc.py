import json
from app.llm import call_llm

async def doc_agent_node(state: dict) -> dict:
    """Scans for missing documentation and docstrings."""
    print("[Documentation Agent] Reviewing docstrings and README changes (Token Optimized)...")
    
    # Extract static documentation findings
    findings = state.get("static_findings", {}).get("documentation", [])
    findings_str = json.dumps(findings, indent=2) if findings else "No missing documentation/docstrings pre-flagged by static analysis."
    
    system_prompt = (
        "You are a Documentation Agent. Your goal is to check if public functions, classes, or modules "
        "have appropriate docstrings and clarify complicated parts of the logic with inline comments.\n\n"
        "To save token costs, you are provided with:\n"
        "1. Repo-scoped documentation standards (e.g. PEP-257 docstring conventions).\n"
        "2. Deterministic new functions missing docstrings pre-checked findings.\n"
        "3. A token-optimized and condensed code diff.\n\n"
        "Your task:\n"
        "- Recommend explicit docstrings or comment changes for functions lacking them.\n"
        "- Suggest docstring additions where missing in the diff.\n\n"
        "Formatting Rules:\n"
        "1. Do NOT use bullet points for findings that contain code blocks. Bullet points cause markdown nesting and indentation bugs.\n"
        "2. Format each suggestion with standard Markdown headings, e.g.:\n"
        "### 📝 Docstring Suggestion for `function_name`\n"
        "3. Always ensure your code blocks are opened and closed correctly using standard triple backticks with a language specifier (e.g. ```python or ```javascript) and are NOT indented."
    )
    
    user_prompt = (
        f"PR Title: {state['pr_title']}\n"
        f"Repository: {state['repo_name']}\n\n"
        f"--- Scoped Repo Memory ---\n{state.get('repo_context', 'None')}\n\n"
        f"--- Pre-Checked Static Findings ---\n{findings_str}\n\n"
        f"--- Optimized Diff Content ---\n{state.get('optimized_diff', '')}"
    )
    
    report = await call_llm(system_prompt, user_prompt)
    return {"documentation_report": report}
