import requests
from bs4 import BeautifulSoup
from langchain_core.tools import tool


@tool
def web_fetch(url: str) -> str:
    """
    Fetch and extract readable text from a webpage.

    Use this when a web search result contains a useful URL
    and you need more detailed information from that page.
    """

    try:
        response = requests.get(
            url,
            timeout=10,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )

        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Remove elements that usually don't contain useful article text
        for element in soup([
            "script",
            "style",
            "nav",
            "footer",
            "header",
            "aside"
        ]):
            element.decompose()

        text = soup.get_text(separator=" ", strip=True)

        # Prevent extremely large webpages from overwhelming Gemini
        return text[:15000]

    except Exception as e:
        return (
            "TOOL_ERROR: Web page fetch failed.\n"
            f"Reason: {str(e)}"
        )