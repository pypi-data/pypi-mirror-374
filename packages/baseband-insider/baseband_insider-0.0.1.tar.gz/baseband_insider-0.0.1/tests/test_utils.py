from __future__ import annotations

import json

from baseband_insider.protocol import MetaEvent
from baseband_insider.utils import drop_none, now_ms, serialize_event


class TestUtils:
    def test_now_ms_monotonic(self) -> None:
        a = now_ms()
        b = now_ms()
        assert isinstance(a, float)
        assert b >= a

    def test_drop_none_recursive(self) -> None:
        value = {"a": 1, "b": None, "c": [1, None, {"d": None, "e": 2}]}
        cleaned = drop_none(value)
        assert cleaned == {"a": 1, "c": [1, {"e": 2}]}

    def test_serialize_event_json(self) -> None:
        evt = MetaEvent(request_id="abc123")
        s = serialize_event(evt)
        payload = json.loads(s)
        assert payload["event_type"] == "meta_event"
        assert payload["request_id"] == "abc123"
        assert isinstance(payload["timestamp"], float)
