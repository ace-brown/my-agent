from rich import print
from rich.markup import escape


def on_event(event):
    """Show a short line in the terminal for each tool the agent runs.

    Args:
        event: What happened, such as the tool name, what it was asked for,
            what it returned, and whether it failed or was skipped.
    """

    if event["error"]:
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
