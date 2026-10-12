from dotenv import load_dotenv
from anthropic import Anthropic
from my_agent.agent import run_agent


def run():
    """Start the agent from the command line."""

    load_dotenv()

    client = Anthropic()

    result = run_agent(
        client,
        "Compare the first paragraphs of https://en.wikipedia.org/wiki/Python_(programming_language) and https://en.wikipedia.org/wiki/Rust",
    )

    print(result)
