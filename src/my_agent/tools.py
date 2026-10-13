import os
import httpx
import trafilatura
from dotenv import load_dotenv

MAX_CHARS = 10_000

FETCH_PAGE_TOOL = {
    "name": "fetch_page",
    "description": (
        "Get the main readable text of a web page. "
        "Use this when you need the content of a specific URL. "
        "Long pages are truncated. "
        "If the page can't be fetched, returns a short error message."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "Full URL of the page, including https://",
            },
        },
        "required": ["url"],
    },
}

WEB_SEARCH_TOOL = {
    "name": "web_search",
    "description": (
        "Search the web for the query. "
        "Use this when you need info or page and you don't know which URL has the answer. "
        "It returns a numbered list of results each with url, title and snippet. "
        "Snippets are short, so you should use fetch_page tool to fetch the most promising URLs. "
        "If the search fails or finds nothing, returns a short message."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Short search keywords, like you'd type into a search engine",
            },
        },
        "required": ["query"],
    },
}


def fetch_page(url: str) -> str:
    """Get the main text of a web page.

    Args:
        url: The page to fetch.

    Returns:
        The page text, cut to MAX_CHARS characters if it's longer.
        If the page can't be fetched or has no text, a short message
        saying what went wrong.
    """
    try:
        res = httpx.get(
            url,
            follow_redirects=True,
            headers={
                "User-Agent": "my-agent/0.1(https://github.com/ace-brown/my-agent)"
            },
            timeout=10,
        )
        res.raise_for_status()
    except httpx.HTTPError as exc:
        return f"Could not get the text for {url} - {exc}"

    html = res.text

    result = trafilatura.extract(html)

    if not result:
        return f"No readable text found at {url}"

    if len(result) > MAX_CHARS:
        truncated_result = (
            result[:MAX_CHARS] + f"\n\nTruncated: showing first {MAX_CHARS} characters"
        )
        return truncated_result

    return result


def web_search(query: str) -> str:
    """Search the web.

    Args:
        query: What to search for.

    Returns:
        A numbered list of results, each with a title, URL, and short snippet.
        If the search fails or finds nothing, a short message saying so.
    """
    api_key = os.environ["TAVILY_API_KEY"]

    try:
        res = httpx.post(
            url="https://api.tavily.com/search",
            headers={"Authorization": f"Bearer {api_key}"},
            json={"query": query, "max_results": 5},
            timeout=10,
        )
        res.raise_for_status()
    except httpx.HTTPError as exc:
        return f"Search failed for '{query}': {exc}"

    data = res.json()

    formatted_results = []

    if not data["results"]:
        return f"No results for '{query}'"

    for number, item in enumerate(data["results"], start=1):
        formatted_content = " ".join(item["content"].split())
        formatted_results.append(
            f"[{number}] {item['title']}\nURL: {item['url']}\n{formatted_content}"
        )

    return "\n\n".join(formatted_results)


if __name__ == "__main__":
    load_dotenv()
    result = web_search("best Python web frameworks 2026")
    print(result)
