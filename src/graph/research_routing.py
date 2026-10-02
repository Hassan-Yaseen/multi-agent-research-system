from src.config import MAX_TOOL_CALLS
from src.state.state import AgentState


def research_router(state: AgentState):

    if state["tool_calls"] >= MAX_TOOL_CALLS:
        return "extract"

    last_message = state["messages"][-1]

    if getattr(last_message, "tool_calls", None):
        return "tools"

    return "extract"