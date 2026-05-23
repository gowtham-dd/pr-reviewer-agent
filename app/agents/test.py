from app.llm import call_llm

async def test_agent_node(state: dict) -> dict:
    """Suggests test cases and highlights missing coverage."""
    print("[Test Agent] Checking test coverage and drafting test templates...")
    system_prompt = (
        "You are a Senior QA and Testing Agent. Review this code diff and identify missing test coverage "
        "for new logic, edge cases that require tests, and provide a concrete boilerplate unit test suite "
        "using `pytest` that the developer can directly copy-paste.\n\n"
        "Formatting Rules:\n"
        "1. Do NOT use bullet points for findings that contain code blocks. Bullet points cause markdown nesting and indentation bugs.\n"
        "2. Format your test cases and coverage gaps with standard Markdown headings, e.g.:\n"
        "### 🧪 Missing Coverage / Boilerplate Tests\n"
        "3. Always ensure your Python code blocks are opened and closed correctly using standard triple backticks: ```python and ```."
    )
    user_prompt = f"PR Title: {state['pr_title']}\nRepository: {state['repo_name']}\n\nDiff Content:\n{state['diff']}"
    report = await call_llm(system_prompt, user_prompt)
    return {"test_report": report}
