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


def ask_claude(client: Anthropic, messages: list, on_event):
    """Send the conversation to Claude, with research instructions and the web tools.

    Args:
        client: The Anthropic client to use.
        messages: The whole conversation so far.
        on_event: Called with each piece of Claude's reply as it arrives.

    Returns:
        Claude's full response.
    """

    with client.messages.stream(
        max_tokens=4096,
        messages=messages,
        model="claude-haiku-5-5",
        system=SYSTEM_PROMPT,
        cache_control={"type": "ephemeral"},
        tools=[FETCH_PAGE_TOOL, WEB_SEARCH_TOOL],
    ) as stream:
        for text in stream.text_stream:
            on_event({"event_type": EventType.TEXT, "text": text})

        return stream.get_final_message()


def run_agent(client: Anthropic, question: str, on_event):
    """Let Claude answer a question, using tools as many times as it needs.

    Pages that were already read are not fetched again, and searches and
    page fetches are capped per run. If a tool crashes, Claude is told about
    the error and the run keeps going.

    Args:
        client: The Anthropic client to use.
        question: The user's question.
        on_event: Called with an event before each call to Claude, each
            time a tool is used, and once at the end with the total tokens
            used, so the caller can show progress.

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
    token_input = 0
    token_output = 0
    cached_tokens = 0

    returned_result = "Stopped: too many steps"

    for _ in range(10):
        on_event({"event_type": EventType.THINKING})
        response = ask_claude(client, conversation, on_event)
        token_input += response.usage.input_tokens
        token_output += response.usage.output_tokens
        cached_tokens += response.usage.cache_read_input_tokens or 0

        conversation.append({"role": "assistant", "content": response.content})

        # Claude is done (no tools asked for): build the final result and leave the round loop.
        if response.stop_reason != "tool_use":
            # Block loop: only find the text of the reply (there may be none).
            text = ""
            for block in response.content:
                if block.type == "text":
                    text = block.text
                    break

            if not text:
                returned_result = f"No answer was written: {response.stop_reason}"
            elif response.stop_reason == "max_tokens":
                returned_result = (
                    "⚠️ This report was cut off and is incomplete.\n\n" + text
                )
            elif response.stop_reason == "end_turn":
                returned_result = text
            else:
                returned_result = (
                    text + f"\n\nIt has stopped because of {response.stop_reason}"
                )
            break

        tool_results = []
        # Loop for when it's tool_use
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

    on_event(
        {
            "event_type": EventType.USAGE,
            "usage": {
                "token_input": token_input,
                "token_output": token_output,
                "cached_tokens": cached_tokens,
            },
        }
    )
    return returned_result
