from dotenv import load_dotenv
from anthropic import Anthropic
from my_agent.agent import run_agent
from my_agent.report import save_report
from my_agent.cli import on_event


def run():
    """Start the agent from the command line."""

    load_dotenv()

    client = Anthropic()

    query = "What is the latest important news of today?"

    result = run_agent(client, query, on_event)

    save_report(result, query)

    print("Report saved to reports folder.")
