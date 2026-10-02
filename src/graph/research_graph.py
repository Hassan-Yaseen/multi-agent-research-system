from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import HumanMessage

from src.state.state import AgentState

from src.tools.search import web_search
from src.tools.fetch import web_fetch

from src.nodes.researcher import researcher_node
from src.nodes.research_extractor import research_extractor_node

from src.graph.research_routing import research_router


TOOLS = [
    web_search,
    web_fetch,
]

tool_node = ToolNode(TOOLS)


def initialize_research(state: AgentState) -> AgentState:

    if state["messages"]:
        return state

    return {
        **state,
        "messages": [
            HumanMessage(content=state["query"])
        ],
    }


def build_research_graph():

    graph = StateGraph(AgentState)

    graph.add_node(
        "initialize",
        initialize_research,
    )

    graph.add_node(
        "researcher",
        researcher_node,
    )

    graph.add_node(
        "tools",
        tool_node,
    )

    graph.add_node(
        "extract",
        research_extractor_node,
    )

    graph.add_edge(
        START,
        "initialize",
    )

    graph.add_edge(
        "initialize",
        "researcher",
    )

    graph.add_conditional_edges(
        "researcher",
        research_router,
        {
            "tools": "tools",
            "extract": "extract",
        },
    )

    graph.add_edge(
        "tools",
        "researcher",
    )

    graph.add_edge(
        "extract",
        END,
    )

    return graph.compile()