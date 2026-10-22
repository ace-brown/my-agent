import argparse
import os
import sys
from dotenv import find_dotenv, load_dotenv
from anthropic import Anthropic, APIConnectionError, APIStatusError, AuthenticationError
from my_agent.agent import run_agent
from my_agent.report import save_report
from my_agent.cli import on_event, show_error

REQUIRED_KEYS = ["ANTHROPIC_API_KEY", "TAVILY_API_KEY"]


def run():
    """Research the question given on the command line and save the report."""

    # Look for .env in the folder the command is run from, so it also works
    # after installing the tool (the code then lives far from the user's files).
    load_dotenv(find_dotenv(usecwd=True))

    parser = argparse.ArgumentParser(
        description="Research a question on the web and write a Markdown report with sources."
    )
    parser.add_argument("question", help="the question to research")
    args = parser.parse_args()

    missing_keys = [key for key in REQUIRED_KEYS if not os.environ.get(key)]
    if missing_keys:
        show_error(
            f"Missing {', '.join(missing_keys)}. "
            "Set it in your environment or in a .env file in this folder "
            "(see .env.example)."
        )
        sys.exit(1)

    client = Anthropic()

    try:
        result = run_agent(client, args.question, on_event)
    except AuthenticationError:
        show_error("Your ANTHROPIC_API_KEY was rejected. Check the key in your .env file.")
        sys.exit(1)
    except APIConnectionError:
        show_error("Could not reach the Claude API. Check your connection and try again.")
        sys.exit(1)
    except APIStatusError as exc:
        show_error(f"The Claude API returned an error ({exc.status_code}). Try again later.")
        sys.exit(1)

    report_path = save_report(result, args.question)

    print(f"Report saved to {report_path}")
