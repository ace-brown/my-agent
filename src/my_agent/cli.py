from rich import print
from rich.markup import escape
from my_agent.events import EventType

# True while Claude's streamed text has left the cursor in the middle of a line.
_mid_line = False


def on_event(event):
    """Show a short line in the terminal for each step of the agent.

    Args:
        event: What happened, like a piece of Claude's reply, Claude
            starting to think, or a tool being used along with what it was
            asked for, what it returned, and whether it failed or was skipped.
    """
    global _mid_line

    if event["event_type"] == EventType.TEXT:
        print(escape(event["text"]), end="", flush=True)
        _mid_line = True
        return

    # Start cursor line on a fresh line after streamed text.
    if _mid_line:
        print()
        _mid_line = False

    if event["event_type"] == EventType.THINKING:
        label = "🤔 Thinking…"
        details = ""
    elif event["error"]:
        label = "❌ [bold red]Error[/bold red]"
        details = f"[red]{escape(event['tool_content'][:80])}[/red]"
    elif event["skipped"]:
        label = "⏭️  [yellow]Skipped[/yellow]"
        details = f"[dim]{escape(event['input'].get('url') or event['input'].get('query'))}[/dim]"
    elif event["tool_name"] == "web_search":
        label = "🔍 [bold cyan]Searching[/bold cyan]"
        details = escape(event["input"]["query"])
    else:
        label = "📄 [bold green]Reading[/bold green]"
        details = escape(event["input"]["url"])
    print(f"{label} {details}")


def show_error(message):
    """Show a short error line in the terminal.

    Args:
        message: What went wrong, in plain words.
    """
    global _mid_line

    if _mid_line:
        print()
        _mid_line = False

    print(f"❌ [bold red]{escape(message)}[/bold red]")
