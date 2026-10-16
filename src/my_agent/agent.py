from anthropic import Anthropic
from my_agent.tools import FETCH_PAGE_TOOL, WEB_SEARCH_TOOL, TOOLS_REGISTRY

SYSTEM_PROMPT = """\
You are a research agent. To answer a question, search the web, read the most \
relevant pages, and only then write the answer.

Citations:
- Cite every important fact with a number in brackets, like [1].
- Only cite pages you actually read with the fetch_page tool, never pages you \
only saw in search results.

Write the answer as a Markdown report with exactly this layout:

# <A short title that fits the question>

## Summary
<2-4 sentences that answer the question directly, with citations.>

## <Section heading that fits the topic>
<Details, as short paragraphs or bullet points, with citations.>

<Add more ## sections as needed. Choose headings that fit the question.>

## Sources
- [1] <Page title> - <URL>
- [2] <Page title> - <URL>
"""


def ask_claude(client: Anthropic, messages: list):
    """Send the conversation to Claude, with research instructions and the web tools.

    Args:
        client: The Anthropic client to use.
        messages: The whole conversation so far.

    Returns:
        Claude's full response.
    """
    message = client.messages.create(
        max_tokens=4096,
        messages=messages,
        model="claude-haiku-5-5",
        system=SYSTEM_PROMPT,
        tools=[FETCH_PAGE_TOOL, WEB_SEARCH_TOOL],
    )

    return message


def run_agent(client: Anthropic, question: str):
    """Let Claude answer a question, using tools as many times as it needs.

    Pages that were already read are not fetched again.

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

    fetched_urls = []

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
                url = block.input.get("url")

                if block.name not in TOOLS_REGISTRY:
                    tool_content = f"Unknown tool: {block.name}"
                elif url is not None and url in fetched_urls:
                    tool_content = "You already read this page. Its content is earlier in the conversation."
                else:
                    tool_content = TOOLS_REGISTRY[block.name](**block.input)
                    if block.name == "fetch_page":
                        fetched_urls.append(url)
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": tool_content,
                    }
                )

        conversation.append({"role": "user", "content": tool_results})

    return "Stopped: too many steps"
