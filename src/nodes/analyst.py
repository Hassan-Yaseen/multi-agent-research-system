from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage

from src.config import GOOGLE_API_KEY
from src.state.state import AgentState
from src.utils.content import extract_text


llm = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash",
    google_api_key=GOOGLE_API_KEY,
)


ANALYST_PROMPT = """
You are the Analyst Agent in a multi-agent research system.

Your job is to analyze structured research evidence collected by
the Research Agent.

You do NOT perform web searches.

You must analyze the provided evidence and produce a structured
analysis for the Critic and Synthesis agents.

Focus on:

1. The most important findings.
2. Facts directly supported by sources.
3. Agreement between different sources.
4. Contradictions or inconsistencies.
5. Source quality and authority.
6. Information that may be outdated.
7. Important details that are still missing.
8. The evidence that should be used in the final answer.

Do not invent information.

Do not add facts that are not present in the research evidence.

Clearly distinguish between:
- directly supported facts
- reasonable interpretation
- uncertainty or missing information

Do not write the final user-facing answer.

User query:

{query}

Research evidence:

{research_results}

Sources:

{sources}
"""


def analyst_node(state: AgentState) -> AgentState:

    research_text = ""

    for i, result in enumerate(
        state["research_results"],
        start=1
    ):
        research_text += (
            f"\n\nSOURCE {i}\n"
            f"Title: {result['title']}\n"
            f"URL: {result['url']}\n"
            f"Content: {result['content']}"
        )

    prompt = ANALYST_PROMPT.format(
        query=state["query"],
        research_results=research_text,
        sources="\n".join(state["sources"]),
    )

    try:
        response = llm.invoke(
            [
                SystemMessage(content=prompt),
                HumanMessage(
                    content="Analyze the research evidence."
                ),
            ]
        )

        text = extract_text(response.content)

        return {
            **state,
            "analysis": text,
            "current_agent": "analyst",
            "next_agent": "critic",
            "iteration": state["iteration"] + 1,
        }

    except Exception as e:

        print(
            f"[Analyst Error] {type(e).__name__}: {str(e)}"
        )

        return {
            **state,
            "analysis": (
                "Analysis could not be completed because "
                f"the Analyst Agent encountered an error: {str(e)}"
            ),
            "current_agent": "analyst",
            "next_agent": "synthesis",
            "iteration": state["iteration"] + 1,
        }