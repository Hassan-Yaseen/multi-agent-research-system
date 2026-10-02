from langchain_core.tools import tool
from ddgs import DDGS


@tool
def web_search(query: str) -> str:
    """Search the web for current or up-to-date information.

    Use this tool when the user asks about current events,
    recent information, prices, products, companies, or other
    information that may have changed over time.
    """

    try:
        results = DDGS().text(
            query,
            max_results=5,
        )

        if not results:
            return "No search results found."

        formatted_results = []

        for result in results:
            formatted_results.append(
                f"Title: {result.get('title', '')}\n"
                f"URL: {result.get('href', '')}\n"
                f"Snippet: {result.get('body', '')}"
            )

        return "\n\n".join(formatted_results)

    except Exception as e:
        return (
            "TOOL_ERROR: Web search failed.\n"
            f"Reason: {str(e)}"
        )