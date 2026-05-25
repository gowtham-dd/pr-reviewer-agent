from app.core.token_optimizer import parse_and_optimize_diff, run_deterministic_checks, get_repo_scoped_memory

async def orchestrator_node(state: dict) -> dict:
    """Initializes the review process, runs static analysis, and optimizes diff tokens."""
    print(f"[Orchestrator] Starting token-optimized review pipeline for PR: {state['pr_title']} in {state['repo_name']}")
    
    # 1. Optimize code diff (filter lockfiles, compress unchanged context, truncate if needed)
    print("[Orchestrator] Optimizing diff size and stripping noise...")
    optimized = parse_and_optimize_diff(state["diff"])
    
    # 2. Run deterministic static analysis before invoking the LLM
    print("[Orchestrator] Executing deterministic pre-checks...")
    findings = run_deterministic_checks(state["diff"], state["repo_name"])
    
    # 3. Retrieve repo-scoped memory context (WHERE repo = active_repo)
    print(f"[Orchestrator] Loading repo-scoped memory for {state['repo_name']}...")
    memory_context = get_repo_scoped_memory(state["repo_name"])
    
    return {
        "status": "running",
        "optimized_diff": optimized,
        "static_findings": findings,
        "repo_context": memory_context
    }
