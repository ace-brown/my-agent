from my_agent.report import save_report


def test_report(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    text = (
        "# Python 3.14: What's New\n"
        "\n"
        "## Summary\n"
        "Python 3.14 adds template strings [1].\n"
        "\n"
        "## Sources\n"
        "- [1] What's New in Python 3.14 - https://docs.python.org/3/whatsnew/3.14.html\n"
    )
    question = "What is new in Python 3.14?"
    report_path = save_report(text, question)

    assert report_path.exists()

    assert report_path.suffix == ".md"

    assert report_path.parent.name == "reports"

    assert report_path.read_text(encoding="utf-8") == text
