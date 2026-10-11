from anthropic import Anthropic
from my_agent.tools import FETCH_PAGE_TOOL


def ask_claude(client: Anthropic, question: str):
    """Send a question to Claude, with the fetch_page tool available.

    Args:
        client: The Anthropic client to use.
        question: What to ask Claude.

    Returns:
        Claude's full response.
    """
    message = client.messages.create(
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": question,
            }
        ],
        model="claude-haiku-5-5",
        tools=[FETCH_PAGE_TOOL],
    )

    return message
