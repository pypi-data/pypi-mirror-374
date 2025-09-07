from __future__ import annotations

from baseband_insider import Capsule, Section, Text, Url, event_stack


class TestProtocolBasics:
    def test_loading_setter_emits_only_loading_patch(self) -> None:
        with event_stack() as stack:
            sec = Section(id="s1", loading=True)
            before = len(stack.events)
            sec.set_loading(False)
            assert len(stack.events) == before + 1
            evt = stack.events[-1].data
            assert evt.type == "section"
            assert evt.loading is False
            assert evt.folded is None
            assert evt.title is None

    def test_folded_setter_emits_only_folded_patch(self) -> None:
        with event_stack() as stack:
            sec = Section(id="s1", folded=False)
            before = len(stack.events)
            sec.set_folded(True)
            assert len(stack.events) == before + 1
            evt = stack.events[-1].data
            assert evt.type == "section"
            assert evt.folded is True
            assert evt.loading is None
            assert evt.title is None

    def test_title_setter_emits_only_title_patch(self) -> None:
        with event_stack() as stack:
            sec = Section(id="s1")
            before = len(stack.events)
            sec.set_title("New")
            assert len(stack.events) == before + 1
            evt = stack.events[-1].data
            assert evt.type == "section"
            assert evt.title == "New"
            assert evt.loading is None
            assert evt.folded is None

    def test_capsule_and_text_emit(self) -> None:
        with event_stack() as stack:
            sec = Section(id="s1")
            Capsule(parent=sec, title="Doc", target=Url("https://example.com"))
            t = Text(parent=sec)
            t.append("hello")

        kinds = [e.data.type for e in stack.events]
        assert "capsule" in kinds
        assert kinds[-1] == "text"
