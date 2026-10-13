from dotenv import load_dotenv
from anthropic import Anthropic
from my_agent.agent import run_agent
from my_agent.report import save_report


def run():
    """Start the agent from the command line."""

    load_dotenv()

    client = Anthropic()

    result = run_agent(
        client, "What new features were added in the latest Django release?"
    )

    save_report(result)
