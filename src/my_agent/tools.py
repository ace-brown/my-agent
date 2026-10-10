import httpx
import trafilatura

MAX_CHARS = 10_000


def fetch_page(url: str) -> str:
    """Get the main text of a web page.

    Args:
        url: The page to fetch.

    Returns:
        The page text, cut to MAX_CHARS characters if it's longer,
        or a short message if the page has no text.
    """
    res = httpx.get(
        url,
        follow_redirects=True,
        headers={"User-Agent": "my-agent/0.1(https://github.com/ace-brown/my-agent)"},
    )

    res.raise_for_status()

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


if __name__ == "__main__":
    # print(fetch_page("https://kraftmeister.org"))
    print(fetch_page("https://en.wikipedia.org/wiki/Malcolm_X"))
