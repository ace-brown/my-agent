from anthropic import Anthropic
from my_agent.tools import FETCH_PAGE_TOOL, WEB_SEARCH_TOOL, TOOLS_REGISTRY


def ask_claude(client: Anthropic, messages: list):
    """Send the conversation to Claude, with the web tools available.

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
        tools=[FETCH_PAGE_TOOL, WEB_SEARCH_TOOL],
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

                if block.name not in TOOLS_REGISTRY:
                    tool_content = f"Unknown tool: {block.name}"
                else:
                    tool_content = TOOLS_REGISTRY[block.name](**block.input)
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": tool_content,
                    }
                )

        conversation.append({"role": "user", "content": tool_results})

    return "Stopped: too many steps"
