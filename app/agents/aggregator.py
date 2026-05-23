async def aggregator_node(state: dict) -> dict:
    """Merges parallel agent reports into a consolidated Markdown report."""
    print("[Aggregator] Consolidating reports...")
    
    summary = f"""# 🤖 AI Automated Code Review Report

| 📁 Repository | 📝 Pull Request | 👤 Author | 🚦 Pipeline Status |
| :--- | :--- | :--- | :--- |
| `{state['repo_name']}` | **{state['pr_title']}** | @{state['author']} | `Gate Approval Completed` |

---

## 🔍 Security Analysis
{state.get('security_report', 'Pending security scan...')}

---

## 📐 Code Quality & Architecture
{state.get('quality_report', 'Pending quality scan...')}

---

## 🧪 Test Coverage & Recommendations
{state.get('test_report', 'Pending test coverage check...')}

---

## 📝 Documentation & Docstrings
{state.get('documentation_report', 'Pending doc check...')}

---
*Review compiled successfully. Awaiting human moderator authorization.*
"""
    return {
        "consolidated_report": summary,
        "status": "pending"
    }
