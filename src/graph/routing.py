from langgraph.graph import END

from src.config import (
    MAX_ITERATIONS,
    MAX_RESEARCH_ROUNDS,
)

from src.state.state import AgentState


def supervisor_router(state: AgentState):

    if state["iteration"] >= MAX_ITERATIONS:
        return END

    next_agent = state["next_agent"]

    if next_agent == "research":

        if state["research_round"] >= MAX_RESEARCH_ROUNDS:
            return "analyst"

        return "researcher"

    if next_agent == "analyst":
        return "analyst"

    if next_agent == "critic":
        return "critic"

    if next_agent == "synthesis":
        return "synthesis"

    return END