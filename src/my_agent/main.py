from dotenv import load_dotenv
from anthropic import Anthropic
from my_agent.agent import run_agent
from my_agent.report import save_report


def run():
    """Start the agent from the command line."""

    load_dotenv()

    client = Anthropic()

    query = "What new features were added in the latest nextJs release?"
    # query = "What are the best crypto and coins to buy for 5x or more gain?"

    result = run_agent(client, query)

    save_report(result, query)

    print("Report saved to reports folder.")
