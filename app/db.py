import json
import os
from typing import Dict, List, Any, Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_FILE = os.path.join(BASE_DIR, "reviews.json")
CI_DB_FILE = os.path.join(BASE_DIR, "ci_failures.json")
ISSUES_DB_FILE = os.path.join(BASE_DIR, "issues.json")

def init_db():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f)
    if not os.path.exists(CI_DB_FILE):
        with open(CI_DB_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f)
    if not os.path.exists(ISSUES_DB_FILE):
        with open(ISSUES_DB_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f)

def get_all_reviews() -> Dict[str, Any]:
    init_db()
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_all_reviews(reviews: Dict[str, Any]):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(reviews, f, indent=2)

def get_review(pr_id: str) -> Optional[Dict[str, Any]]:
    return get_all_reviews().get(pr_id)

def save_review(pr_id: str, data: Dict[str, Any]):
    reviews = get_all_reviews()
    reviews[pr_id] = data
    save_all_reviews(reviews)

def delete_review(pr_id: str):
    reviews = get_all_reviews()
    if pr_id in reviews:
        del reviews[pr_id]
        save_all_reviews(reviews)

# --- CI/CD Failures Storage ---

def get_all_ci_failures() -> Dict[str, Any]:
    init_db()
    try:
        with open(CI_DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_all_ci_failures(failures: Dict[str, Any]):
    with open(CI_DB_FILE, "w", encoding="utf-8") as f:
        json.dump(failures, f, indent=2)

def get_ci_failure(workflow_id: str) -> Optional[Dict[str, Any]]:
    return get_all_ci_failures().get(workflow_id)

def save_ci_failure(workflow_id: str, data: Dict[str, Any]):
    failures = get_all_ci_failures()
    failures[workflow_id] = data
    save_all_ci_failures(failures)

def delete_ci_failure(workflow_id: str):
    failures = get_all_ci_failures()
    if workflow_id in failures:
        del failures[workflow_id]
        save_all_ci_failures(failures)


# --- Issues Storage ---

def get_all_issues() -> Dict[str, Any]:
    init_db()
    try:
        with open(ISSUES_DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_all_issues(issues: Dict[str, Any]):
    with open(ISSUES_DB_FILE, "w", encoding="utf-8") as f:
        json.dump(issues, f, indent=2)

def get_issue(issue_id: str) -> Optional[Dict[str, Any]]:
    return get_all_issues().get(issue_id)

def save_issue(issue_id: str, data: Dict[str, Any]):
    issues = get_all_issues()
    issues[issue_id] = data
    save_all_issues(issues)

def delete_issue(issue_id: str):
    issues = get_all_issues()
    if issue_id in issues:
        del issues[issue_id]
        save_all_issues(issues)
