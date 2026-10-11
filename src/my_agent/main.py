from dotenv import load_dotenv
from anthropic import Anthropic
from my_agent.agent import ask_claude


def run():

    load_dotenv()

    client = Anthropic()

    message = ask_claude(
        client,
        "Tell me two first years that you can find in the Malcom X's first wiki page",
    )

    print(message.stop_reason)

    print(message.to_json())
