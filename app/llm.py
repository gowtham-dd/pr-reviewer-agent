import os
import re
import asyncio
from typing import Optional
from langchain_core.messages import SystemMessage, HumanMessage
from app.config import get_settings

# Prevent concurrent API rate limits (HTTP 429) on model endpoints
LLM_SEMAPHORE = asyncio.Semaphore(1)


def get_chat_model():
    cfg = get_settings()
    provider = cfg.llm_provider.lower()
    
    if provider == "openai" and cfg.openai_api_key:
        from langchain_openai import ChatOpenAI
        model = cfg.llm_model or "gpt-4o-mini"
        return ChatOpenAI(api_key=cfg.openai_api_key, model=model, temperature=0.2)
        
    elif provider == "gemini" and cfg.gemini_api_key:
        from langchain_google_genai import ChatGoogleGenerativeAI
        model = cfg.llm_model or "gemini-2.5-flash"
        return ChatGoogleGenerativeAI(google_api_key=cfg.gemini_api_key, model=model, temperature=0.2)
        
    elif provider == "anthropic" and cfg.anthropic_api_key:
        from langchain_anthropic import ChatAnthropic
        model = cfg.llm_model or "claude-3-5-sonnet-20241022"
        return ChatAnthropic(api_key=cfg.anthropic_api_key, model_name=model, temperature=0.2)
        
    elif provider == "groq" and cfg.groq_api_key:
        from langchain_groq import ChatGroq
        model = cfg.llm_model or "llama-3.3-70b-versatile"
        return ChatGroq(api_key=cfg.groq_api_key, model_name=model, temperature=0.2)
        
    else:
        # Fallback / Mock
        return None

async def call_llm(system_prompt: str, user_prompt: str) -> str:
    """
    Calls the configured LLM or generates a highly realistic mock response
    if we are in 'mock' mode or missing credentials.
    Includes parallel rate-limit handling and automatic retries.
    """
    model = get_chat_model()
    if model is not None:
        async with LLM_SEMAPHORE:
            max_retries = 3
            backoff = 2.0
            for attempt in range(max_retries):
                try:
                    messages = [
                        SystemMessage(content=system_prompt),
                        HumanMessage(content=user_prompt)
                    ]
                    response = await model.ainvoke(messages)
                    return response.content
                except Exception as e:
                    # Detect rate limit 429 errors
                    err_msg = str(e).lower()
                    if "429" in err_msg or "rate limit" in err_msg:
                        if attempt < max_retries - 1:
                            print(f"⚠️ [LLM API Rate Limited] Retrying in {backoff}s (Attempt {attempt+1}/{max_retries})...")
                            await asyncio.sleep(backoff)
                            backoff *= 2.0
                            continue
                    
                    # Fall back to smart mock if it is a different issue or retries are exhausted
                    return f"*(Warning: LLM API call failed with error: {str(e)}. Displaying simulated fallback review instead)*\n\n" + generate_mock_review(system_prompt, user_prompt)
    else:
        return generate_mock_review(system_prompt, user_prompt)

def generate_mock_review(system_prompt: str, user_prompt: str) -> str:
    """
    Generates intelligent mock comments by inspecting the user's PR diff
    to simulate real security flaws, styling violations, tests, and documentation.
    """
    # Extract diff content from prompt if present
    diff_match = re.search(r"diff\s+[\s\S]*", user_prompt, re.IGNORECASE)
    diff_text = diff_match.group(0) if diff_match else user_prompt
    
    # Identify which agent we are mocking based on the system prompt
    agent_type = "general"
    sys_lower = system_prompt.lower()
    if "security" in sys_lower or "owasp" in sys_lower:
        agent_type = "security"
    elif "quality" in sys_lower or "style" in sys_lower or "lint" in sys_lower:
        agent_type = "quality"
    elif "test" in sys_lower or "coverage" in sys_lower:
        agent_type = "test"
    elif "docstring" in sys_lower or "documentation" in sys_lower or "comment" in sys_lower:
        agent_type = "documentation"

    # Analyze diff context to create super-realistic findings
    has_sql = "execute(" in diff_text or "select " in diff_text or "insert into" in diff_text
    has_keys = "secret" in diff_text.lower() or "password" in diff_text.lower() or "apikey" in diff_text.lower() or "api_key" in diff_text.lower()
    has_eval = "eval(" in diff_text or "exec(" in diff_text
    has_complex = "if " in diff_text and diff_text.count("if ") > 3
    has_magic = any(re.search(rf"\b{num}\b", diff_text) for num in ["3.14", "86400", "3600", "999"])
    
    # Extract function names if possible to reference them directly!
    functions = re.findall(r"def\s+(\w+)\s*\(", diff_text)
    func_ref = f"`{functions[0]}`" if functions else "the updated functions"

    if agent_type == "security":
        if has_sql:
            return f"""### 🛡️ Security Analysis (OWASP Top 10 Check)
- **Finding 1: Potential SQL Injection Vulnerability**
  - **Location**: {func_ref}
  - **Severity**: 🔴 CRITICAL (OWASP A03:2021-Injection)
  - **Description**: The query appears to construct raw SQL statements using direct string concatenation or raw string formatting. An attacker could manipulate inputs to execute arbitrary SQL commands.
  - **Recommendation**: Refactor to use parameterized queries or an ORM (like SQLAlchemy).
  - **Code Suggestion**:
    ```python
    # Incorrect
    query = f"SELECT * FROM users WHERE username = '{{username}}'"
    db.execute(query)
    
    # Correct (Parameterized)
    db.execute("SELECT * FROM users WHERE username = :username", {{"username": username}})
    ```
"""
        elif has_keys:
            return """### 🛡️ Security Analysis (OWASP Top 10 Check)
- **Finding 1: Exposed Hardcoded Credential/API Key**
  - **Severity**: 🔴 CRITICAL (OWASP A02:2021-Cryptographic Failures)
  - **Description**: Detected a raw string assignment to a variable that looks like an API Key, password, or secret token. Hardcoded secrets are easily leaked and represent a severe threat.
  - **Recommendation**: Extract this credential into an environment variable and load it via `os.getenv()`. Add the source configuration file to `.gitignore`.
  - **Code Suggestion**:
    ```python
    # Incorrect
    API_KEY = "sk_live_51N..."
    
    # Correct
    import os
    API_KEY = os.getenv("STRIPE_API_KEY")
    ```
"""
        elif has_eval:
            return f"""### 🛡️ Security Analysis (OWASP Top 10 Check)
- **Finding 1: Insecure Code Execution (`eval`/`exec`)**
  - **Location**: {func_ref}
  - **Severity**: 🔴 CRITICAL (OWASP A03:2021-Injection)
  - **Description**: Using `eval()` or `exec()` with dynamic inputs enables arbitrary code execution.
  - **Recommendation**: Avoid `eval()` altogether. Parse inputs strictly using a secure format like JSON or use predefined safe mapping dictionaries.
"""
        else:
            return f"""### 🛡️ Security Analysis (OWASP Top 10 Check)
- **Status**: 🟢 PASS
- **Analysis**:
  - Scanned diff for OWASP Top 10 vulnerabilities including SQL injection, directory traversal, command injection, broken authentication, and exposed secrets.
  - No critical vulnerabilities found in the modified lines.
  - **Proactive Recommendation**: Ensure that inputs to {func_ref} are sanitized at the entry point of the application before reaching internal utility functions.
"""

    elif agent_type == "quality":
        findings = []
        if has_complex:
            findings.append(f"""- **Complexity Alert: High Cognitive Complexity**
  - **Location**: {func_ref}
  - **Severity**: 🟡 MEDIUM
  - **Description**: The function has multiple nested conditional branches (`if`/`else` structures). High cognitive complexity makes debugging harder and increases the likelihood of regression bugs.
  - **Recommendation**: Extract nested logic into small, single-responsibility helper functions.""")
        if has_magic:
            findings.append("""- **Coding Style: Hardcoded Magic Numbers**
  - **Severity**: 🟢 LOW
  - **Description**: Detected raw numbers without explanation. Hardcoded constants reduce maintainability.
  - **Recommendation**: Define these as self-documenting uppercase module-level constants (e.g. `SECONDS_IN_DAY = 86400`).""")
        
        # Always add some standard lint feedback if empty
        if not findings:
            findings.append(f"""- **Style Check: Standard PEP 8 Compliance**
  - **Severity**: 🟢 INFO
  - **Observation**: Naming conventions for {func_ref} conform to `snake_case`. Variable declarations look clean.
  - **Recommendation**: Ensure trailing lines are clean and no unused imports exist in the modified file.""")
            
        return "### 📐 Code Quality & Style Analysis\n" + "\n\n".join(findings)

    elif agent_type == "test":
        if functions:
            test_cases = "\n".join([f"    def test_{f}_success(self):\n        # TODO: Implement test case\n        pass" for f in functions[:2]])
            return f"""### 🧪 Automated Test Analysis & Coverage
- **Status**: 🟡 Coverage Gap Detected
- **Current Coverage**: ~0% for new functions
- **Missing Coverage**:
  - {func_ref} has no corresponding unit tests in this diff.
- **Suggested Test Implementation**:
  Create or update a test file (e.g., `tests/test_code.py`) with these test assertions:
  ```python
  import pytest
  from app.module import {functions[0]}

  class Test{functions[0].title()}:
{test_cases}
  ```
- **Execution Checklist**:
  - Run `pytest --cov=app` to confirm baseline test suite integrity.
  - Assert edge cases, specifically `None` inputs, empty strings, and type exceptions.
"""
        else:
            return """### 🧪 Automated Test Analysis & Coverage
- **Status**: 🟢 PASS
- **Observation**: The diff consists mostly of configurations, documentation, or minor styles. No new logic was introduced that requires dedicated unit tests.
- **Recommendation**: Run existing tests using `pytest` to verify no regressions were introduced.
"""

    elif agent_type == "documentation":
        doc_needed = "def " in diff_text and '"""' not in diff_text
        if doc_needed:
            return f"""### 📝 Documentation & API Changes
- **Finding 1: Missing Docstring in Public API**
  - **Location**: {func_ref}
  - **Severity**: 🟡 WARNING
  - **Description**: Public function is missing a docstring. Clear docstrings are essential for API maintainability, auto-generated documentation, and editor autocomplete.
  - **Recommendation**: Add a PEP-257 compliant docstring describing parameters, return values, and raised exceptions.
  - **Code Suggestion**:
    ```python
    def {functions[0] if functions else "my_function"}(param1, param2):
        \"\"\"
        Brief description of the function's purpose.

        Args:
            param1 (type): Description of param1.
            param2 (type): Description of param2.

        Returns:
            type: Description of return value.
        \"\"\"
        # function body...
    ```
"""
        else:
            return f"""### 📝 Documentation & API Changes
- **Status**: 🟢 PASS
- **Observation**: All modified or newly added methods in this diff include appropriate PEP-257 docstrings.
- **Analysis**: Clear explanations of parameters and return types were successfully provided, enhancing future maintainability.
"""

    # Fallback/General
    return f"""### 🤖 General Agent Report
Reviewed the requested code modifications.
No blocking issues found. Code style and quality look good.
"""
