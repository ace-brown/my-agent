# my-agent: a web research agent built from scratch

> 🚧 **Work in progress.** I'm building this step by step. See the [roadmap](#roadmap) for what is done and what is next.

Ask a question, and the agent searches the web, reads the most useful pages, and writes a Markdown report with citations.

It is built **from scratch on the [Anthropic Python SDK](https://github.com/anthropics/anthropic-sdk-python)**, with no LangChain or other agent framework. The agent loop, the tools, and the guardrails are all written by hand, so every part of how the agent works is visible in the code.

## How it works

```
1. Plan     → Claude breaks the question into smaller questions
2. Search   → web_search tool   → titles, URLs, snippets
3. Read     → fetch_page tool   → clean main text of a page
4. Reflect  → enough information? conflicting sources? → search again
5. Write    → Markdown report with numbered citations [1], [2], …
```

At the center is a simple loop: send the conversation and the tool definitions to Claude → Claude asks to use a tool → the code runs it and sends the result back → repeat until Claude gives a final answer.

## Tools

| Tool | What it does | Status |
|---|---|---|
| `fetch_page(url)` | Downloads a page and returns only its main readable text | ✅ working |
| `web_search(query)` | Returns the top search results for a query | ⏳ planned |

## Design decisions

- **No framework.** Writing the agent loop myself makes it clear how tool use works: what Claude sends, what the code sends back, and when the loop stops.
- **Clean text, not raw HTML.** [trafilatura](https://github.com/adbar/trafilatura) strips menus, ads, and scripts before anything reaches the model. Raw HTML is mostly noise and wastes tokens.
- **Page length limit.** Page text is cut to `MAX_CHARS` characters, with a note telling Claude the page was truncated. The API is stateless, so every page already read is sent again on every later call. Without a limit, one long page could make a whole research session expensive.
- **Tools always answer in words.** When a page has no readable text, the tool returns a short message instead of `None`, so Claude understands what happened and can try another source.
- **Honest User-Agent.** Requests identify the agent with a descriptive `User-Agent` header (name, version, link to this repo) instead of the default `python-httpx/…` or a fake browser string. Many sites, Wikipedia included, block anonymous scripts with `403 Forbidden` and ask automated tools to identify themselves. Being upfront about what the tool is is the respectful way to read other people's websites.

## Getting started

You need Python 3.10+ and an [Anthropic API key](https://console.anthropic.com/). The agent runs on **your own key**, and nothing is hosted.

```bash
git clone https://github.com/ace-brown/my-agent.git
cd my-agent

uv sync                     # or: python -m venv .venv && pip install -e .
cp .env.example .env        # then put your key in .env
```

```bash
uv run web-search
```

## Roadmap

- [x] Project setup and a first call to Claude
- [ ] Agent loop with the `fetch_page` tool *(in progress)*
- [ ] `web_search` tool
- [ ] Research prompt and Markdown reports with citations
- [ ] Guardrails: step and search limits, error handling, retries
- [ ] Live terminal output showing each step
- [ ] Context management and token/cost summary
- [ ] Tests and a small evaluation set
- [ ] Demo GIF and example reports

## License

MIT
