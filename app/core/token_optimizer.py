import re
import os
import json
from typing import Dict, List, Optional

# --- Lockfiles and Noisy Files to Filter Out ---
FILTERED_PATTERNS = [
    r"package-lock\.json",
    r"yarn\.lock",
    r"pnpm-lock\.yaml",
    r"uv\.lock",
    r"poetry\.lock",
    r"Gemfile\.lock",
    r"go\.sum",
    r"\.min\.js",
    r"\.min\.css",
    r"\.svg",
    r"\.png",
    r"\.jpg",
    r"\.jpeg",
    r"\.gif",
    r"\.ico",
    r"\.woff2?",
    r"\.map$"
]

# --- Static Memory Storage Simulation for Multi-Repo Isolation ---
# In production, this would load from PostgreSQL or Qdrant scoped by 'repo_name'
MEMORIES_DIR = "memory"

DEFAULT_MEMORIES = {
    "payment-service": {
        "architecture": "Microservice for Stripe/PayPal payment integrations. Uses Redis distributed locks for idempotency.",
        "conventions": "Must use Decimal for currency computations. Never print raw API response payloads to stdout.",
        "api_contracts": "Exposes /v1/payments (POST) and /v1/refunds (POST). Requires Bearer authorization token."
    },
    "analytics-engine": {
        "architecture": "OLAP database processing system using PostgreSQL TimescaleDB. Integrates with Kafka stream consumers.",
        "conventions": "All aggregate SQL queries must be heavily optimized and utilize indexing keys. Use snake_case column names.",
        "api_contracts": "Exposes /analytics/metrics (GET) and /analytics/ingest (POST)."
    },
    "mobile-app": {
        "architecture": "React Native frontend wrapper with offline synchronization capabilities using SQLite WatermelonDB.",
        "conventions": "Follow strict ESLint rules and use custom hooks for data fetching. Leverage React Native FastImage.",
        "api_contracts": "Consumes payment-service and analytics-engine REST APIs."
    }
}

def parse_and_optimize_diff(raw_diff: str, max_chars: int = 12000) -> str:
    """
    Parses a git diff, filters out package locks/binaries, deletes noisy 
    context lines, and limits character count to stay within hard token budgets.
    """
    if not raw_diff or raw_diff.strip() == "Unavailable diff details (GitHub API credentials or connection not active)":
        return "No diff content to analyze."

    optimized_lines = []
    current_file_ignored = False
    
    lines = raw_diff.splitlines()
    for line in lines:
        # Check if we are starting a new file in the diff
        if line.startswith("diff --git"):
            current_file_ignored = False
            # Check if this file name matches any filtered patterns
            for pattern in FILTERED_PATTERNS:
                if re.search(pattern, line, re.IGNORECASE):
                    current_file_ignored = True
                    optimized_lines.append(f"--- [Token Optimization: File analysis skipped for lockfile/binary: {line.split('/')[-1]}] ---")
                    break
        
        if current_file_ignored:
            continue
            
        # Optimization: Exclude standard unchanged context lines (lines starting with ' ') 
        # to save up to 40% of the diff token size, retaining only metadata headers and modifications (+/-).
        if line.startswith(" ") and not (line.startswith("+++") or line.startswith("---")):
            # Skip standard unchanged context
            continue
            
        optimized_lines.append(line)
        
    optimized_text = "\n".join(optimized_lines)
    
    # Enforce Hard Token Budget Limit (character truncation as a proxy for tokens)
    if len(optimized_text) > max_chars:
        print(f"⚠️ [Token Optimizer] Diff size ({len(optimized_text)} chars) exceeds maximum budget. Truncating...")
        truncated_msg = f"\n\n... [TRUNCATED BY TOKEN OPTIMIZER to fit {max_chars} character limit] ..."
        optimized_text = optimized_text[:max_chars - len(truncated_msg)] + truncated_msg
        
    return optimized_text


def run_deterministic_checks(raw_diff: str, repo_name: str) -> Dict[str, List[Dict]]:
    """
    Executes standard, deterministic parsing checks directly on the diff BEFORE 
    any LLM call occurs. Categorizes issues by Security, Quality, Documentation, and Tests.
    """
    findings = {
        "security": [],
        "quality": [],
        "documentation": [],
        "test": []
    }
    
    if not raw_diff or "diff --git" not in raw_diff:
        return findings

    # Parse raw diff into files and hunks
    current_file = "unknown"
    line_number = 0
    
    # Vulnerability regexes
    SECRET_REGEXES = [
        (r"(?i)(api_key|apikey|secret|password|auth_token)\s*=\s*['\"][a-zA-Z0-9_\-+=/]{16,}['\"]", "Hardcoded credentials/secrets in source code"),
        (r"sk_live_[a-zA-Z0-9]{24}", "Stripe Secret Live API Key exposed"),
        (r"AIzaSy[a-zA-Z0-9_\-]{33}", "Google API Key exposed")
    ]
    
    lines = raw_diff.splitlines()
    for i, line in enumerate(lines):
        if line.startswith("diff --git"):
            match = re.search(r"b/(.+)$", line)
            current_file = match.group(1) if match else "unknown"
            line_number = 0
            continue
            
        if line.startswith("@@"):
            # Parse start line
            match = re.search(r"\+(\d+)", line)
            line_number = int(match.group(1)) if match else 0
            continue
            
        if line.startswith("-"):
            # Deletion, do not increment added lines counter
            continue
            
        if line.startswith("+") and not line.startswith("+++"):
            # This is an added line
            code_line = line[1:].strip()
            
            # --- 1. Deterministic Security Checks ---
            # Secret Exposure Check
            for regex, description in SECRET_REGEXES:
                if re.search(regex, code_line):
                    findings["security"].append({
                        "file": current_file,
                        "line": line_number,
                        "severity": "CRITICAL",
                        "title": "Exposed Hardcoded API Key/Secret",
                        "description": f"{description}. Storing raw secrets in repositories is insecure.",
                        "recommendation": "Use environment variables (`os.getenv()`) and configure a git-secrets scanner.",
                        "snippet": code_line
                    })
            
            # SQL Injection Check (naive concatenation)
            if "execute(" in code_line or "db.execute(" in code_line or "raw(" in code_line:
                if "%" in code_line or ".format(" in code_line or "f\"" in code_line or "f'" in code_line:
                    if "select" in code_line.lower() or "insert" in code_line.lower() or "update" in code_line.lower():
                        findings["security"].append({
                            "file": current_file,
                            "line": line_number,
                            "severity": "HIGH",
                            "title": "Potential SQL Injection",
                            "description": "Found string formatting or concatenation inside an database execution statement.",
                            "recommendation": "Use parameterized queries or an ORM mapper to automatically bind inputs securely.",
                            "snippet": code_line
                        })
            
            # Unsafe execution Check
            if "eval(" in code_line or "exec(" in code_line:
                findings["security"].append({
                    "file": current_file,
                    "line": line_number,
                    "severity": "HIGH",
                    "title": "Unsafe Dynamic Code Execution",
                    "description": "Usage of `eval()` or `exec()` detected with potentially untrusted inputs.",
                    "recommendation": "Remove eval/exec usage. Use explicit mappings or robust parsing structures (like `json.loads`).",
                    "snippet": code_line
                })
                
            # --- 2. Deterministic Quality Checks ---
            # Cognitive Nesting Check
            if code_line.startswith(("if ", "elif ")) and i >= 2:
                # Look back to see indentation count / nesting levels
                indentation = len(line[1:]) - len(code_line)
                if indentation >= 12: # Usually equivalent to 3 levels of nested tabs/spaces
                    findings["quality"].append({
                        "file": current_file,
                        "line": line_number,
                        "severity": "MEDIUM",
                        "title": "High Cognitive Complexity",
                        "description": "Deeply nested conditional block (3+ levels of indentation) makes code harder to understand.",
                        "recommendation": "Decompose nested conditions and extract complex code segments into single-purpose methods.",
                        "snippet": code_line
                    })
                    
            # Magic Numbers Check
            if any(num in code_line for num in ["86400", "3600", "3.1415", "604800"]):
                if not code_line.isupper() and "=" in code_line: # Avoid triggering on constant declarations
                    findings["quality"].append({
                        "file": current_file,
                        "line": line_number,
                        "severity": "LOW",
                        "title": "Magic Number Usage",
                        "description": "Hardcoded magic numbers were used directly in the executable code body.",
                        "recommendation": "Define these numeric parameters as descriptive, uppercase constants at the top of the file.",
                        "snippet": code_line
                    })

            # --- 3. Deterministic Documentation Checks ---
            if code_line.startswith("def ") or code_line.startswith("class "):
                # Look at subsequent lines in the diff to see if a docstring exists
                has_docstring = False
                for j in range(i + 1, min(i + 4, len(lines))):
                    next_line = lines[j]
                    if next_line.startswith("+") and ('"""' in next_line or "'''" in next_line):
                        has_docstring = True
                        break
                if not has_docstring and not code_line.startswith("def test_"):
                    findings["documentation"].append({
                        "file": current_file,
                        "line": line_number,
                        "severity": "WARNING",
                        "title": "Missing Docstring",
                        "description": f"The newly defined method/class `{code_line.split('(')[0]}` is missing a PEP-257 docstring.",
                        "recommendation": "Add a descriptive docstring summarizing parameters, behavior, exceptions, and return values.",
                        "snippet": code_line
                    })
            
            # --- 4. Deterministic Test Coverage Check ---
            if code_line.startswith("def ") and not code_line.startswith("def test_") and "test" not in current_file.lower():
                func_name = code_line.split("def ")[1].split("(")[0]
                # We can check if a test file is being added/modified in the diff
                test_exists = False
                for other_line in lines:
                    if other_line.startswith("diff --git") and "test" in other_line.lower():
                        test_exists = True
                        break
                if not test_exists:
                    findings["test"].append({
                        "file": current_file,
                        "line": line_number,
                        "severity": "MEDIUM",
                        "title": "Coverage Gap",
                        "description": f"New function `{func_name}` has been added, but no accompanying unit tests were found in this PR diff.",
                        "recommendation": f"Add a corresponding test function `test_{func_name}` inside a new or existing test module to cover this logic.",
                        "snippet": code_line
                    })

            line_number += 1
            
    return findings


def get_repo_scoped_memory(repo_name: str) -> str:
    """
    Implements Repo-Scoped Memory Isolation. Resolves vector/file storage
    specifically restricted to the requested repo_name (WHERE repo = repo_name).
    """
    # 1. Attempt to load from directory filesystem
    repo_slug = re.sub(r"[^a-zA-Z0-9_\-]", "_", repo_name)
    repo_file = os.path.join(MEMORIES_DIR, repo_slug, "context.json")
    
    if os.path.exists(repo_file):
        try:
            with open(repo_file, "r") as f:
                data = json.load(f)
                return (
                    f"--- Repository-Scoped Memory context resolved for '{repo_name}' ---\n"
                    f"Architecture: {data.get('architecture', 'N/A')}\n"
                    f"Conventions: {data.get('conventions', 'N/A')}\n"
                    f"API Contracts: {data.get('api_contracts', 'N/A')}\n"
                )
        except Exception as e:
            print(f"⚠️ [Memory Loader] Failed to read scoped memory for {repo_name}: {e}")
            
    # 2. Fallback to predefined memories to guarantee seamless baseline behavior
    for key, value in DEFAULT_MEMORIES.items():
        if key in repo_name.lower():
            return (
                f"--- Repository-Scoped Memory context resolved for '{repo_name}' (Isolated Memory) ---\n"
                f"Architecture: {value['architecture']}\n"
                f"Conventions: {value['conventions']}\n"
                f"API Contracts: {value['api_contracts']}\n"
            )
            
    return (
        f"--- Repository-Scoped Memory context resolved for '{repo_name}' ---\n"
        f"Architecture: General software repository.\n"
        f"Conventions: standard clean code, naming conventions, proper error handling.\n"
    )
