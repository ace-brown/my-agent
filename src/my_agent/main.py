import argparse
from dotenv import load_dotenv
from anthropic import Anthropic
from my_agent.agent import run_agent
from my_agent.report import save_report
from my_agent.cli import on_event


def run():
    """Research the question given on the command line and save the report."""

    load_dotenv()

    parser = argparse.ArgumentParser(
        description="Research a question on the web and write a Markdown report with sources."
    )
    parser.add_argument("question", help="the question to research")
    args = parser.parse_args()

    client = Anthropic()

    result = run_agent(client, args.question, on_event)

    save_report(result, args.question)

    print("Report saved to reports folder.")
