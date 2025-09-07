from __future__ import annotations

import json
import time
from dataclasses import asdict
from typing import TYPE_CHECKING
from uuid import uuid4

if TYPE_CHECKING:
    from .protocol import MessageEvent


def now_ms() -> float:
    """Return current UTC timestamp in microseconds since epoch as float.

    Provides sub-millisecond precision to avoid duplicate timestamps
    while staying within JavaScript's safe integer limits.
    """
    return time.time() * 1_000_000


def gen_id() -> str:
    """Generate a compact unique id for nodes/events."""
    return uuid4().hex


def drop_none(value):
    """Recursively remove None values from dicts and lists."""
    if isinstance(value, dict):
        return {k: drop_none(v) for k, v in value.items() if v is not None}
    if isinstance(value, list):
        return [drop_none(v) for v in value if v is not None]
    return value


def serialize_event(event: "MessageEvent") -> str:
    """Serialize a MessageEvent dataclass (with nested dataclasses) to a JSON string.

    Removes fields with None values for a cleaner payload.
    """
    return json.dumps(drop_none(asdict(event)))
