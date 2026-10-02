from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage

from src.config import GOOGLE_API_KEY
from src.state.state import AgentState


llm = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash",
    google_api_key=GOOGLE_API_KEY,
)


SUPERVISOR_PROMPT = """
You are the Supervisor Agent in a multi-agent research system.

Your job is to coordinate the workflow.

Available agents:

- research
  Performs web research and gathers factual evidence.

- analyst
  Analyzes the collected research evidence, identifies important
  findings, comparisons, patterns, and possible conflicts.

- critic
  Evaluates whether the research and analysis are sufficient,
  relevant, supported, and internally consistent.

- synthesis
  Produces the final user-facing answer.

You must choose exactly ONE next action:

research
analyst
critic
synthesis

Workflow rules:

1. If there is no research evidence, choose research.

2. If research exists but there is no analysis yet, choose analyst.

3. If analysis exists but there is no critique yet, choose critic.

4. If the critic says the research is insufficient, unsupported,
   outdated, or contains unresolved important contradictions,
   choose research.

5. If the critic approves the research and analysis, choose synthesis.

6. Do not choose synthesis unless the critic has approved the work.

7. Do not choose analyst again unless new research has been added.

8. Do not choose critic again unless analysis has been produced or
   updated.

9. Do not perform research yourself.

10. Return ONLY one word:
research
analyst
critic
synthesis

Current workflow state:

Research available:
{has_research}

Number of research results:
{research_count}

Analysis available:
{has_analysis}

Critique available:
{has_critique}

Critique passed:
{critique_passed}

Research complete:
{research_complete}

Iteration:
{iteration}

User query:
{query}
"""


def supervisor_node(state: AgentState) -> AgentState:

    prompt = SUPERVISOR_PROMPT.format(
        has_research=bool(state["research_results"]),
        research_count=len(state["research_results"]),
        has_analysis=bool(state["analysis"]),
        has_critique=bool(state["critique"]),
        critique_passed=state["critique_passed"],
        research_complete=state["research_complete"],
        iteration=state["iteration"],
        query=state["query"],
    )

    try:
        response = llm.invoke(
            [
                SystemMessage(content=prompt),
                HumanMessage(
                    content="Determine the next workflow action."
                ),
            ]
        )

        # Gemini may return content as a list of content blocks
        if isinstance(response.content, list):
            content = ""

            for block in response.content:
                if isinstance(block, dict):
                    content += block.get("text", "")
                else:
                    content += str(block)
        else:
            content = str(response.content)

        next_agent = content.strip().lower()

        # Safety fallback
        valid_agents = {
            "research",
            "analyst",
            "critic",
            "synthesis",
        }

        if next_agent not in valid_agents:
            next_agent = "research"

        return {
            **state,
            "current_agent": "supervisor",
            "next_agent": next_agent,
        }

    except Exception as e:

        print(
            f"[Supervisor Error] {type(e).__name__}: {str(e)}"
        )

        return {
            **state,
            "current_agent": "supervisor",
            "next_agent": "research",
        }