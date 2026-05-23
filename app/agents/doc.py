from app.llm import call_llm

async def doc_agent_node(state: dict) -> dict:
    """Scans for missing documentation and docstrings."""
    print("[Documentation Agent] Reviewing docstrings and README changes...")
    system_prompt = (
        "You are a Documentation Agent. Check if public functions, classes, or modules added/modified in "
        "the diff have PEP-257 docstrings and clarify complicated parts of the logic with clear inline comments. "
        "Suggest actual docstring additions where missing.\n\n"
        "Formatting Rules:\n"
        "1. Do NOT use bullet points for findings that contain code blocks. Bullet points cause markdown nesting and indentation bugs.\n"
        "2. Format each suggestion with standard Markdown headings, e.g.:\n"
        "### 📝 Docstring Suggestion for `function_name`\n"
        "3. Always ensure your code blocks are opened and closed correctly using standard triple backticks with a language specifier (e.g. ```python or ```javascript) and are NOT indented."
    )
    user_prompt = f"PR Title: {state['pr_title']}\nRepository: {state['repo_name']}\n\nDiff Content:\n{state['diff']}"
    report = await call_llm(system_prompt, user_prompt)
    return {"documentation_report": report}
