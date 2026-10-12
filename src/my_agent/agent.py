from anthropic import Anthropic
from my_agent.tools import FETCH_PAGE_TOOL, fetch_page


def ask_claude(client: Anthropic, messages: list):
    """Send the conversation to Claude, with the fetch_page tool available.

    Args:
        client: The Anthropic client to use.
        messages: The whole conversation so far.

    Returns:
        Claude's full response.
    """
    message = client.messages.create(
        max_tokens=1024,
        messages=messages,
        model="claude-haiku-5-5",
        tools=[FETCH_PAGE_TOOL],
    )

    return message


def run_agent(client: Anthropic, question: str):
    """Let Claude answer a question, using tools as many times as it needs.

    Args:
        client: The Anthropic client to use.
        question: The user's question.

    Returns:
        Claude's final answer, or a short message if it took too many steps.
    """

    conversation = [
        {
            "role": "user",
            "content": question,
        },
    ]

    for _ in range(10):
        response = ask_claude(client, conversation)

        conversation.append({"role": "assistant", "content": response.content})

        if response.stop_reason != "tool_use":
            for block in response.content:
                if block.type == "text":
                    return block.text

        tool_results = []

        for block in response.content:
            if block.type == "tool_use":
                url = block.input["url"]
                page_text = fetch_page(url)
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": page_text,
                    }
                )

        conversation.append({"role": "user", "content": tool_results})

    return "Stopped: too many steps"
