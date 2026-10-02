from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage

from src.config import GOOGLE_API_KEY
from src.state.state import AgentState
from src.utils.content import extract_text


llm = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash",
    google_api_key=GOOGLE_API_KEY,
)


CRITIC_PROMPT = """
You are the Critic Agent in a multi-agent research system.

Your job is to evaluate the quality of the research and analysis
before the final answer is generated.

Evaluate:

1. Whether the research answers the user's question.
2. Whether important claims are supported by sources.
3. Whether the sources are sufficiently reliable.
4. Whether there are contradictions between sources.
5. Whether important information is missing.
6. Whether the analysis accurately reflects the research.
7. Whether additional research is necessary.

You must make a final decision:

PASS
or
FAIL

Use FAIL when:
- important evidence is missing
- important claims are unsupported
- major contradictions remain unresolved
- the research is clearly insufficient
- the analysis misrepresents the evidence

Use PASS when the evidence is sufficient for a reliable final answer.

Your response MUST use exactly this format:

DECISION: PASS

REASON:
<concise explanation>

RESEARCH_GAPS:
<important remaining gaps, or "None">

Do not write the final answer.

User query:

{query}

Research evidence:

{research_results}

Analysis:

{analysis}
"""


def critic_node(state: AgentState) -> AgentState:

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

    prompt = CRITIC_PROMPT.format(
        query=state["query"],
        research_results=research_text,
        analysis=state["analysis"],
    )

    try:
        response = llm.invoke(
            [
                SystemMessage(content=prompt),
                HumanMessage(
                    content="Critically evaluate the research."
                ),
            ]
        )

        critique = extract_text(response.content)

        critique_passed = parse_critic_decision(
            critique
        )

        return {
            **state,
            "critique": critique,
            "critique_passed": critique_passed,
            "current_agent": "critic",
            "next_agent": (
                "synthesis"
                if critique_passed
                else "research"
            ),
            "iteration": state["iteration"] + 1,
        }

    except Exception as e:

        print(
            f"[Critic Error] {type(e).__name__}: {str(e)}"
        )

        return {
            **state,
            "critique": (
                "Critique could not be completed because "
                f"the Critic Agent encountered an error: {str(e)}"
            ),
            "critique_passed": False,
            "current_agent": "critic",
            "next_agent": "research",
            "iteration": state["iteration"] + 1,
        }


def parse_critic_decision(text) -> bool:

    if isinstance(text, list):

        text_parts = []

        for block in text:

            if isinstance(block, str):
                text_parts.append(block)

            elif isinstance(block, dict):
                if "text" in block:
                    text_parts.append(block["text"])

        text = "\n".join(text_parts)

    if not isinstance(text, str):
        return False

    first_lines = text.upper().splitlines()

    for line in first_lines:

        if line.strip().startswith("DECISION:"):

            decision = line.split(
                ":", 1
            )[1].strip()

            return decision == "PASS"

    # Conservative fallback
    return False