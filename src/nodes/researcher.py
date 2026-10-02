from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage

from src.config import GOOGLE_API_KEY
from src.state.state import AgentState
from src.tools.search import web_search
from src.tools.fetch import web_fetch


llm = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash",
    google_api_key=GOOGLE_API_KEY,
)

TOOLS = [
    web_search,
    web_fetch,
]

research_llm = llm.bind_tools(TOOLS)


RESEARCHER_PROMPT = """
You are the Research Agent in a multi-agent research system.

Your job is to research the user's question using the available tools.

Available tools:

- web_search: search the web
- web_fetch: read a webpage

Instructions:

1. Search for relevant information.
2. Use multiple searches when different aspects of the question need
   investigation.
3. Fetch important sources when snippets are insufficient.
4. Prefer authoritative and recent sources.
5. Avoid unnecessary tool calls.
6. Do not produce the final user-facing answer.
7. Gather useful factual evidence for downstream agents.
8. Continue researching until you have enough useful evidence to answer
   the user's question.
9. When you believe sufficient evidence has been gathered, stop calling
   tools and provide a concise research summary.
10. Include important source URLs and factual claims supported by them.
11. Do not write the final user-facing answer.

If previous analysis or critique identifies research gaps, focus your
new research on those gaps instead of repeating the same searches.

Important reliability rules:

- Never treat TOOL_ERROR messages as factual evidence.
- If a webpage cannot be fetched, use another source.
- Do not invent information when sources are unavailable.
- Prefer primary and authoritative sources.
- Cross-check important claims when possible.
- Stop researching when sufficient evidence has been collected.

User query:

{query}

Existing research:

{research_results}

Previous analysis:

{analysis}

Previous critique:

{critique}
"""


def researcher_node(state: AgentState) -> AgentState:

    system_prompt = RESEARCHER_PROMPT.format(
        query=state["query"],
        research_results=state["research_results"],
        analysis=state["analysis"],
        critique=state["critique"],
    )

    messages = [
        SystemMessage(content=system_prompt),
        *state["messages"],
    ]

    try:
        response = research_llm.invoke(messages)

        tool_calls = (
            getattr(response, "tool_calls", None)
            or []
        )

        return {
            **state,
            "messages": [response],
            "current_agent": "researcher",
            "research_complete": not bool(tool_calls),
            "iteration": state["iteration"] + 1,
            "tool_calls": (
                state["tool_calls"]
                + len(tool_calls)
            ),
        }

    except Exception as e:

        print(
            f"[Researcher Error] {type(e).__name__}: {str(e)}"
        )

        return {
            **state,
            "research_complete": True,
            "current_agent": "researcher",
            "next_agent": (
                "analyst"
                if state["research_results"]
                else "synthesis"
            ),
            "iteration": state["iteration"] + 1,
        }