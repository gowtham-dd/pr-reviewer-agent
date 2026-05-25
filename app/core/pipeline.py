from typing import TypedDict, Optional
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from app.db import save_review, get_review
from app.agents.orchestrator import orchestrator_node
from app.agents.security import security_agent_node
from app.agents.quality import quality_agent_node
from app.agents.test import test_agent_node
from app.agents.doc import doc_agent_node
from app.agents.aggregator import aggregator_node
from app.agents.publisher import publish_report_node

class ReviewState(TypedDict):
    pr_id: str
    pr_title: str
    repo_name: str
    author: str
    diff: str
    security_report: str
    quality_report: str
    test_report: str
    documentation_report: str
    consolidated_report: str
    status: str        # 'running', 'pending', 'approved', 'rejected', 'completed'
    decision: str      # 'approved', 'rejected'
    feedback: str      # comments from human reviewer
    installation_id: Optional[int]
    optimized_diff: str
    static_findings: dict
    repo_context: str

# --- Graph Assembly ---

workflow = StateGraph(ReviewState)

# Add Nodes
workflow.add_node("orchestrator", orchestrator_node)
workflow.add_node("security_agent", security_agent_node)
workflow.add_node("quality_agent", quality_agent_node)
workflow.add_node("test_agent", test_agent_node)
workflow.add_node("doc_agent", doc_agent_node)
workflow.add_node("aggregator", aggregator_node)
workflow.add_node("publish_report", publish_report_node)

# Define Edges
workflow.add_edge(START, "orchestrator")

# Parallel branching from Orchestrator to all agents
workflow.add_edge("orchestrator", "security_agent")
workflow.add_edge("orchestrator", "quality_agent")
workflow.add_edge("orchestrator", "test_agent")
workflow.add_edge("orchestrator", "doc_agent")

# Merge back into the aggregator
workflow.add_edge("security_agent", "aggregator")
workflow.add_edge("quality_agent", "aggregator")
workflow.add_edge("test_agent", "aggregator")
workflow.add_edge("doc_agent", "aggregator")

# Interrupt gate: halt right BEFORE entering 'publish_report'
workflow.add_edge("aggregator", "publish_report")
workflow.add_edge("publish_report", END)

# Compile the Graph with checkpointer
checkpointer = MemorySaver()
review_graph = workflow.compile(checkpointer=checkpointer)


# --- Helper Background Tasks ---

async def run_pipeline_task(pr_id: str, pr_title: str, repo_name: str, author: str, diff: str, installation_id: Optional[int] = None):
    """Runs the LangGraph review pipeline up to the interrupt gate."""
    thread_config = {"configurable": {"thread_id": pr_id}}
    
    print(f"\n⚙️  [Pipeline Init] Starting LangGraph Review flow for PR: {pr_title}")
    print(f"🧵 Thread ID / Channel ID: {pr_id}")
    
    # Save initial running status to DB
    save_review(pr_id, {
        "pr_id": pr_id,
        "pr_title": pr_title,
        "repo_name": repo_name,
        "author": author,
        "diff": diff,
        "status": "running",
        "installation_id": installation_id,
        "security_report": "Analyzing...",
        "quality_report": "Analyzing...",
        "test_report": "Analyzing...",
        "documentation_report": "Analyzing...",
        "consolidated_report": "",
        "decision": None,
        "feedback": None
    })
    print("💾 [Pipeline] Saved initial 'running' review state to local DB.")

    try:
        inputs = {
            "pr_id": pr_id,
            "pr_title": pr_title,
            "repo_name": repo_name,
            "author": author,
            "diff": diff,
            "status": "running",
            "installation_id": installation_id,
            "optimized_diff": "",
            "static_findings": {},
            "repo_context": "",
            "decision": "approved",
            "feedback": "Automated system review published successfully without human interaction."
        }
        
        print("🧠 [Pipeline] Starting parallel agents execution...")
        async for event in review_graph.astream(inputs, config=thread_config):
            for node_name, output in event.items():
                print(f"⚡ [Graph Node Completed] Node: '{node_name}' finished execution.")
        
        # Once finished, retrieve state values
        state = await review_graph.aget_state(thread_config)
        state_values = state.values
        
        print("⚖️  [Pipeline] Review completed. Saving consolidated report to database...")
        
        # Save consolidated reports to the database
        save_review(pr_id, {
            "pr_id": pr_id,
            "pr_title": pr_title,
            "repo_name": repo_name,
            "author": author,
            "diff": diff,
            "status": "completed",  # Complete, fully published!
            "installation_id": installation_id,
            "security_report": state_values.get("security_report", "No security feedback."),
            "quality_report": state_values.get("quality_report", "No quality feedback."),
            "test_report": state_values.get("test_report", "No test feedback."),
            "documentation_report": state_values.get("documentation_report", "No documentation feedback."),
            "consolidated_report": state_values.get("consolidated_report", ""),
            "decision": "approved",
            "feedback": "Automated system review published successfully without human interaction."
        })
        print(f"🎉 [Pipeline Success] Finished analysis and automatically published review for thread {pr_id}.\n")
        
    except Exception as e:
        print(f"❌ [Pipeline Error] Failed execution: {e}")
        save_review(pr_id, {
            "pr_id": pr_id,
            "pr_title": pr_title,
            "repo_name": repo_name,
            "author": author,
            "diff": diff,
            "status": "failed",
            "error": str(e)
        })

async def resume_pipeline_task(pr_id: str, decision: str, feedback: str):
    """Resumes the LangGraph review pipeline after human input is submitted."""
    thread_config = {"configurable": {"thread_id": pr_id}}
    
    print(f"\n🔄 [Pipeline Resume] Resuming thread {pr_id} with gate decision: {decision.upper()}")
    
    # Retrieve current local review
    review = get_review(pr_id)
    if not review:
        print(f"❌ [Pipeline Error] Cannot resume. PR {pr_id} not found in DB.")
        return

    # Update DB status
    review["status"] = "processing_decision"
    review["decision"] = decision
    review["feedback"] = feedback
    save_review(pr_id, review)

    try:
        # Update the LangGraph thread state with decision values
        print("🧠 [Pipeline] Injecting decision state values into thread context...")
        await review_graph.aupdate_state(
            thread_config,
            {
                "decision": decision,
                "feedback": feedback
            }
        )

        # Resume the graph execution (this will trigger the publish_report node)
        print("🚀 [Pipeline] Resuming execution flow to publisher node...")
        async for event in review_graph.astream(None, config=thread_config):
            for node_name, output in event.items():
                print(f"⚡ [Graph Node Completed] Node: '{node_name}' finished execution.")

        # Retrieve final state
        state = await review_graph.aget_state(thread_config)
        final_values = state.values
        
        # Save final state back to DB
        review["status"] = "completed" if decision == "approved" else "rejected"
        review["consolidated_report"] = final_values.get("consolidated_report", review["consolidated_report"])
        save_review(pr_id, review)
        print(f"🏁 [Pipeline Complete] PR {pr_id} successfully resumed and finished with status: {review['status']}")
        print("="*80 + "\n")

    except Exception as e:
        print(f"❌ [Pipeline Error] Failed to resume: {e}")
        review["status"] = "failed"
        review["error"] = f"Resume failed: {str(e)}"
        save_review(pr_id, review)
