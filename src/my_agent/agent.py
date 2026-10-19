from anthropic import Anthropic
from my_agent.tools import FETCH_PAGE_TOOL, WEB_SEARCH_TOOL, TOOLS_REGISTRY
from my_agent.events import EventType

MAX_SEARCHES = 5
MAX_FETCHES = 6
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


def run_agent(client: Anthropic, question: str, on_event):
    """Let Claude answer a question, using tools as many times as it needs.

    Pages that were already read are not fetched again, and searches and
    page fetches are capped per run. If a tool crashes, Claude is told about
    the error and the run keeps going.

    Args:
        client: The Anthropic client to use.
        question: The user's question.
        on_event: Called with an event each time a tool is used, so the
            caller can show progress.

    Returns:
        Claude's final answer, with a warning on top if it was cut off, or a
        short message if it took too many steps.
    """

    conversation = [
        {
            "role": "user",
            "content": question,
        },
    ]

    fetched_urls = []
    search_count = 0
    fetch_count = 0

    for _ in range(10):
        response = ask_claude(client, conversation)

        conversation.append({"role": "assistant", "content": response.content})

        if response.stop_reason != "tool_use":
            for block in response.content:
                if block.type == "text":
                    if response.stop_reason == "max_tokens":
                        return (
                            "⚠️ This report was cut off and is incomplete.\n\n"
                            + block.text
                        )
                    elif response.stop_reason == "end_turn":
                        return block.text
                    else:
                        return (
                            block.text
                            + f"It has stopped because of {response.stop_reason}"
                        )
            return f"No answer was written: {response.stop_reason}"

        tool_results = []

        for block in response.content:
            if block.type == "tool_use":
                url = block.input.get("url")
                is_error = False
                skipped = False

                if block.name not in TOOLS_REGISTRY:
                    tool_content = f"Unknown tool: {block.name}"
                    is_error = True
                elif url is not None and url in fetched_urls:
                    tool_content = "You already read this page. Its content is earlier in the conversation."
                    skipped = True
                else:
                    if block.name == "fetch_page" and fetch_count >= MAX_FETCHES:
                        tool_content = f"Max number of fetch is {MAX_FETCHES}, please don't fetch anymore and answer with the current fetched pages"
                        skipped = True
                    elif block.name == "web_search" and search_count >= MAX_SEARCHES:
                        tool_content = f"Max number of web search is {MAX_SEARCHES}, please don't search anymore and answer with the current searches"
                        skipped = True
                    else:
                        if block.name == "fetch_page":
                            fetch_count += 1
                        else:
                            search_count += 1

                        try:
                            tool_content = TOOLS_REGISTRY[block.name](**block.input)
                            if block.name == "fetch_page":
                                fetched_urls.append(url)
                        except Exception as exc:
                            tool_content = f"Unexpected error occured: {exc}"
                            is_error = True
                event = {
                    "tool_name": block.name,
                    "event_type": EventType.TOOL_CALL,
                    "input": block.input,
                    "tool_content": tool_content,
                    "error": is_error,
                    "skipped": skipped,
                }
                on_event(event)
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": tool_content,
                        "is_error": is_error,
                    }
                )

        conversation.append({"role": "user", "content": tool_results})

    return "Stopped: too many steps"
