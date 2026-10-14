import re
from datetime import datetime
from pathlib import Path


def save_report(result: str, query: str):
    """Save the agent's answer as a report file in the reports folder.

    Args:
        result: The final answer to save.
        query: The question the answer is for, used in the file name.

    Returns:
        The path of the saved report.
    """
    reports_folder = Path("reports")
    reports_folder.mkdir(parents=True, exist_ok=True)

    query_slug = re.sub(r"[^a-zA-Z0-9]+", "-", query)[:50].strip("-")
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")

    file_path = reports_folder / f"{timestamp}-{query_slug}.md"
    file_path.write_text(result, encoding="utf-8")
    return file_path
