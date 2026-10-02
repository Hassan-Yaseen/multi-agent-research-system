from typing import Annotated, TypedDict

from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages


class ResearchResult(TypedDict):
    title: str
    url: str
    content: str


class AgentState(TypedDict):
    # Original user request
    query: str

    # Agent conversation / working memory
    messages: Annotated[list[AnyMessage], add_messages]

    # Supervisor routing
    current_agent: str
    next_agent: str

    # Research
    research_results: list[ResearchResult]
    sources: list[str]
    research_complete: bool

    # Analysis
    analysis: str

    # Critic
    critique: str
    critique_passed: bool

    # Final response
    final_answer: str

    # Workflow control
    iteration: int
    research_round: int
    tool_calls: int