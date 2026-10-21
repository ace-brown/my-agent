from types import SimpleNamespace
from my_agent import agent


def test_run_agent(monkeypatch):
    fake_response = SimpleNamespace(
        content=[SimpleNamespace(type="text", text="fake content")],
        stop_reason="end_turn",
        usage=SimpleNamespace(
            input_tokens=10,
            output_tokens=5,
            cache_read_input_tokens=0,
        ),
    )

    client = None
    question = "this is fake"

    def on_event(event):
        pass

    def fake_ask_claude(client, messages, on_event):
        return fake_response

    monkeypatch.setattr(agent, "ask_claude", fake_ask_claude)

    result = agent.run_agent(client, question, on_event)

    assert result == "fake content"


def test_run_agent_searches_then_answers(monkeypatch):
    search_response = SimpleNamespace(
        content=[
            SimpleNamespace(
                id="tool_1",
                type="tool_use",
                name="web_search",
                input={"query": "Laravel latest release notes"},
            )
        ],
        stop_reason="tool_use",
        usage=SimpleNamespace(
            input_tokens=10,
            output_tokens=5,
            cache_read_input_tokens=0,
        ),
    )

    answer_response = SimpleNamespace(
        content=[SimpleNamespace(type="text", text="Laravel 13 adds new features")],
        stop_reason="end_turn",
        usage=SimpleNamespace(
            input_tokens=11,
            output_tokens=6,
            cache_read_input_tokens=1,
        ),
    )

    client = None
    question = "this is fake"

    def on_event(event):
        pass

    searched_queries = []

    def fake_web_search(query):
        searched_queries.append(query)
        return "[1] Laravel 13 release notes\nURL: https://laravel.com/docs/releases\nWhat's new in Laravel 13."

    replies_list = [search_response, answer_response]

    def fake_ask_claude(client, messages, on_event):
        return replies_list.pop(0)

    monkeypatch.setitem(agent.TOOLS_REGISTRY, "web_search", fake_web_search)

    monkeypatch.setattr(agent, "ask_claude", fake_ask_claude)

    result = agent.run_agent(client, question, on_event)

    assert result == "Laravel 13 adds new features"

    assert searched_queries == ["Laravel latest release notes"]
