from __future__ import annotations

from baseband_insider import Section, event_stack


class TestEventStackContext:
    def test_sequential_contexts_are_isolated(self) -> None:
        with event_stack() as s1:
            Section(id="A")
            assert len(s1.events) == 1
            assert s1.events[0].data.id == "A"

        with event_stack() as s2:
            Section(id="B")
            assert len(s2.events) == 1
            assert s2.events[0].data.id == "B"

        # Ensure the two stacks did not mix
        assert s1.events[0].data.id == "A"
        assert s2.events[0].data.id == "B"

    def test_nested_contexts_push_to_top_only(self) -> None:
        with event_stack() as outer:
            Section(id="outer-1")
            with event_stack() as inner:
                Section(id="inner-1")
                assert len(inner.events) == 1
                assert inner.events[0].data.id == "inner-1"

            Section(id="outer-2")

        # Outer captured only its own events, not the inner's
        outer_ids = [e.data.id for e in outer.events]
        assert outer_ids == ["outer-1", "outer-2"]
