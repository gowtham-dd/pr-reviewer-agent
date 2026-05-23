from app.llm import call_llm

async def security_agent_node(state: dict) -> dict:
    """Runs security analysis on the code diff using Llama 3.3 via Groq."""
    print("[Security Agent] Analyzing vulnerabilities...")
    system_prompt = (
        "You are an expert Security Code Reviewer specialized in OWASP Top 10, secret detection, "
        "and injection risks. Analyze the following code diff and list security flaws, severe threats, "
        "or exposed credentials.\n\n"
        "Formatting Rules:\n"
        "1. Do NOT use bullet points (e.g. *, -, or numbers) for findings that contain code blocks. Bullet points cause markdown nesting and indentation bugs.\n"
        "2. Format each finding with a standard Markdown heading, e.g.:\n"
        "### 🚨 [SEVERITY] Finding Title\n"
        "3. Provide the vulnerability description, recommendation, and a properly formatted, fenced code block.\n"
        "4. Always ensure code blocks are opened and closed correctly using standard triple backticks with a language specifier (e.g. ```python or ```javascript) and are NOT indented."
    )
    user_prompt = f"PR Title: {state['pr_title']}\nRepository: {state['repo_name']}\n\nDiff Content:\n{state['diff']}"
    report = await call_llm(system_prompt, user_prompt)
    return {"security_report": report}
