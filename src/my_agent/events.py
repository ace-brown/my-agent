from enum import Enum


class EventType(Enum):
    TOOL_CALL = "tool_call"
    REPORT_DONE = "report_done"
    TRUNCATED = "truncated"
    THINKING = "thinking"
    TEXT = "text"
