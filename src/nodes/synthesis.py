from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage

from src.config import GOOGLE_API_KEY
from src.state.state import AgentState
from src.utils.content import extract_text


llm = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash",
    google_api_key=GOOGLE_API_KEY,
)


SYNTHESIS_PROMPT = """
You are the Synthesis Agent in a multi-agent research system.

Your job is to produce the final answer to the user's question.

You have access to:

- the original user query
- structured research evidence
- analyst findings
- critic evaluation
- source URLs

Use only information supported by the research.

Requirements:

1. Directly answer the user's question.
2. Be concise but sufficiently informative.
3. Do not invent facts.
4. Do not mention internal agents or the workflow.
5. Do not mention the Supervisor, Researcher, Analyst, or Critic.
6. Use the Analyst's interpretation where appropriate.
7. Respect the Critic's evaluation.
8. When useful, mention important sources.
9. If uncertainty exists, clearly state it.
10. Do not claim certainty beyond the evidence.

User query:

{query}

Research evidence:

{research_results}

Analysis:

{analysis}

Critic evaluation:

{critique}

Sources:

{sources}
"""


def synthesis_node(state: AgentState) -> AgentState:

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

    prompt = SYNTHESIS_PROMPT.format(
        query=state["query"],
        research_results=research_text,
        analysis=state["analysis"],
        critique=state["critique"],
        sources="\n".join(state["sources"]),
    )

    try:
        response = llm.invoke(
            [
                SystemMessage(content=prompt),
                HumanMessage(
                    content="Produce the final answer."
                ),
            ]
        )

        text = extract_text(response.content)

        return {
            **state,
            "final_answer": text,
            "current_agent": "synthesis",
            "next_agent": "",
            "iteration": state["iteration"] + 1,
        }

    except Exception as e:

        print(
            f"[Synthesis Error] {type(e).__name__}: {str(e)}"
        )

        fallback_answer = (
            "The system collected research successfully, "
            "but the final synthesis step could not be completed.\n\n"
            f"Reason: {str(e)}\n\n"
            "Available sources:\n"
            + "\n".join(state["sources"])
        )

        return {
            **state,
            "final_answer": fallback_answer,
            "current_agent": "synthesis",
            "next_agent": "",
            "iteration": state["iteration"] + 1,
        }