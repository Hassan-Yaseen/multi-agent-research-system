from langgraph.graph import StateGraph, START, END

from src.state.state import AgentState

from src.nodes.supervisor import supervisor_node
from src.nodes.analyst import analyst_node
from src.nodes.critic import critic_node
from src.nodes.synthesis import synthesis_node

from src.graph.research_graph import build_research_graph
from src.graph.routing import supervisor_router
from src.graph.checkpointer import create_checkpointer


def build_graph():

    graph = StateGraph(AgentState)

    research_graph = build_research_graph()

    # Nodes
    graph.add_node(
        "supervisor",
        supervisor_node
    )

    graph.add_node(
        "researcher",
        research_graph
    )

    graph.add_node(
        "analyst",
        analyst_node
    )

    graph.add_node(
        "critic",
        critic_node
    )

    graph.add_node(
        "synthesis",
        synthesis_node
    )

    # START → Supervisor
    graph.add_edge(
        START,
        "supervisor"
    )

    # Supervisor decides where to go
    graph.add_conditional_edges(
        "supervisor",
        supervisor_router,
        {
            "researcher": "researcher",
            "analyst": "analyst",
            "critic": "critic",
            "synthesis": "synthesis",
            END: END,
        },
    )

    # Research → Supervisor
    graph.add_edge(
        "researcher",
        "analyst"
    )

    # Analyst → Critic
    graph.add_edge(
        "analyst",
        "critic"
    )

    # Critic → Supervisor
    graph.add_edge(
        "critic",
        "supervisor"
    )

    # Synthesis → END
    graph.add_edge(
        "synthesis",
        END
    )

    checkpointer = create_checkpointer()

    return graph.compile(checkpointer=checkpointer)