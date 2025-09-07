from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Generator, List

if TYPE_CHECKING:
    from .protocol import MessageEvent


@dataclass
class EventStack:
    # Stores typed message events
    events: List["MessageEvent"] = field(default_factory=list)


_STACK: List[EventStack] = []


@contextmanager
def event_stack() -> Generator[EventStack, None, None]:
    stack = EventStack()
    _STACK.append(stack)
    try:
        yield stack
    finally:
        _STACK.pop()


def current_stack() -> EventStack:
    if not _STACK:
        raise RuntimeError("No active event_stack context")
    return _STACK[-1]
