from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage

from src.config import GOOGLE_API_KEY
from src.state.state import AgentState


llm = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash",
    google_api_key=GOOGLE_API_KEY,
)


EXTRACTION_SYSTEM_PROMPT = """
You are a research evidence extraction agent.

Your job is to analyze completed web research and convert it into
structured research evidence for downstream agents.

Rules:

1. Extract only information actually present in the research.
2. Do not invent facts or URLs.
3. Preserve the original source URLs.
4. Combine information when the same URL appears multiple times.
5. Ignore conversational messages that do not contain useful evidence.
6. Focus on factual findings rather than the final answer.
7. Return each useful source using exactly this format:

SOURCE
Title: <source title>
URL: <source URL>
Content: <important factual information supported by this source>

SOURCE
Title: ...
URL: ...
Content: ...

If no useful sources were found, return:

NO_SOURCES
"""


def research_extractor_node(state: AgentState) -> AgentState:

    messages_text = "\n\n".join(
        [
            f"{type(message).__name__}:\n{message.content}"
            for message in state["messages"]
            if message.content
        ]
    )

    user_prompt = f"""
User query:

{state["query"]}

Completed research conversation:

{messages_text}

Extract the useful research evidence now.
"""

    response = llm.invoke(
        [
            SystemMessage(content=EXTRACTION_SYSTEM_PROMPT),
            HumanMessage(content=user_prompt),
        ]
    )

    research_results = parse_research_results(response.content)

    sources = []

    for result in research_results:
        url = result["url"]

        if url and url not in sources:
            sources.append(url)

    return {
        **state,

        "research_results": research_results,

        "sources": [
            result["url"]
            for result in research_results
            if result.get("url")
        ],

        "research_complete": True,

        "research_round": state["research_round"] + 1,

        # New research invalidates the previous analysis.
        "analysis": "",
        "critique": "",
        "critique_passed": False,

        "current_agent": "researcher",
        "next_agent": "",
    }


def parse_research_results(text) -> list[dict]:

    # Gemini may return content as a list of blocks
    if isinstance(text, list):

        text_parts = []

        for block in text:

            if isinstance(block, str):
                text_parts.append(block)

            elif isinstance(block, dict):

                # Common LangChain/Gemini content format
                if "text" in block:
                    text_parts.append(block["text"])

        text = "\n".join(text_parts)

    # Make sure we have a string
    if not isinstance(text, str):
        return []

    results = []

    blocks = text.split("SOURCE")

    for block in blocks[1:]:

        lines = [
            line.strip()
            for line in block.strip().splitlines()
            if line.strip()
        ]

        title = ""
        url = ""
        content_parts = []
        current_field = None

        for line in lines:

            if line.startswith("Title:"):
                title = line.replace(
                    "Title:", "", 1
                ).strip()
                current_field = "title"

            elif line.startswith("URL:"):
                url = line.replace(
                    "URL:", "", 1
                ).strip()
                current_field = "url"

            elif line.startswith("Content:"):
                content = line.replace(
                    "Content:", "", 1
                ).strip()

                if content:
                    content_parts.append(content)

                current_field = "content"

            elif current_field == "content":
                content_parts.append(line)

        content = " ".join(content_parts).strip()

        if url and content:

            results.append(
                {
                    "title": title,
                    "url": url,
                    "content": content,
                }
            )

    return results