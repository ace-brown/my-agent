from types import SimpleNamespace
from my_agent import agent

fake_response = SimpleNamespace(
    content=[SimpleNamespace(type="text", text="fake content")],
    stop_reason="end_turn",
    usage=SimpleNamespace(
        input_tokens=10,
        output_tokens=5,
        cache_read_input_tokens=0,
    ),
)


def test_run_agent(monkeypatch):

    client = None
    question = "this is fake"

    def on_event(event):
        pass

    def fake_ask_claude(client, messages, on_event):
        return fake_response

    monkeypatch.setattr(agent, "ask_claude", fake_ask_claude)

    result = agent.run_agent(client, question, on_event)

    assert result == "fake content"
