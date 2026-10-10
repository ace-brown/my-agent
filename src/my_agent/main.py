from dotenv import load_dotenv
from anthropic import Anthropic


def run():

    load_dotenv()

    client = Anthropic()

    message = client.messages.create(
        max_tokens=1024,
        messages=[{"role": "user", "content": "Hi"}],
        model="claude-sonnet-5-5",
    )

    for block in message.content:
        if block.type == "text":
            print(block.text)
