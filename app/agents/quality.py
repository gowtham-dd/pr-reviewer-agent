from app.llm import call_llm

async def quality_agent_node(state: dict) -> dict:
    """Runs code styling, formatting, and complexity checks."""
    print("[Code Quality Agent] Checking style and complexity...")
    system_prompt = (
        "You are a specialized Code Quality, PEP-8, and Architecture Agent. Analyze the following code "
        "diff for code style violations, excessive cognitive complexity, magic numbers, poor naming, "
        "or refactoring opportunities.\n\n"
        "Formatting Rules:\n"
        "1. Do NOT use bullet points for findings that contain code blocks. Bullet points cause markdown nesting and indentation bugs.\n"
        "2. Format each finding with a standard Markdown heading, e.g.:\n"
        "### 🔧 [SEVERITY] Finding Title\n"
        "3. Provide descriptions and a properly formatted, fenced code block for suggestions.\n"
        "4. Always ensure code blocks are opened and closed correctly using standard triple backticks with a language specifier (e.g. ```python or ```javascript) and are NOT indented."
    )
    user_prompt = f"PR Title: {state['pr_title']}\nRepository: {state['repo_name']}\n\nDiff Content:\n{state['diff']}"
    report = await call_llm(system_prompt, user_prompt)
    return {"quality_report": report}
