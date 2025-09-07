from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Literal, Optional, Union

from .utils import gen_id, now_ms

if TYPE_CHECKING:
    from .context import EventStack


def _get_current_stack() -> "EventStack":
    from .context import current_stack as _current_stack

    return _current_stack()


# Message event dataclasses (discriminated union)
@dataclass
class BaseEvent:
    # Discriminator is set by subclasses and excluded from __init__
    event_type: str = field(init=False)
    # Numeric timestamp (microseconds since epoch), defaulted post-init
    timestamp: float = 0

    def __post_init__(self) -> None:
        if not self.timestamp:
            self.timestamp = now_ms()


@dataclass
class StatusChangeEvent(BaseEvent):
    event_type: Literal["status_change"] = field(init=False, default="status_change")
    target_status: Literal["waiting_for_connection", "running", "finished", "failed"] = "running"
    # Optional context for status changes (e.g., error information on failures)
    context: Optional["StatusContext"] = None


@dataclass
class StatusContext:
    # Expandable context container; fields are optional by default
    error: Optional[str] = None


@dataclass
class UpstreamDataEvent(BaseEvent):
    event_type: Literal["upstream_data"] = field(init=False, default="upstream_data")
    data: "ProtocolNode" = field(default_factory=dict)  # discriminated union of protocol nodes


@dataclass
class MetaEvent(BaseEvent):
    event_type: Literal["meta_event"] = field(init=False, default="meta_event")
    request_id: str = ""


MessageEvent = Union[StatusChangeEvent, UpstreamDataEvent, MetaEvent]


def serialize_event(event: MessageEvent) -> str:  # re-export for convenience
    from .utils import serialize_event as _ser

    return _ser(event)


MessageEventType = Literal["status_change", "upstream_data", "meta_event"]
MessageStatus = Literal["waiting_for_connection", "running", "finished", "failed"]


########################
# Temporary Protocol nodes (discriminated union for data)
########################


@dataclass
class BaseProtocolEntity:
    """Base class for all protocol entities that need id and timestamp."""

    id: str = field(default_factory=gen_id)
    timestamp: float = field(default_factory=now_ms)


@dataclass
class Url:
    type: Literal["url"] = field(init=False, default="url")
    url: str = ""


@dataclass
class SectionNode(BaseProtocolEntity):
    type: Literal["section"] = field(init=False, default="section")
    parentId: Optional[str] = None
    icon: Optional[str] = None
    title: Optional[str] = None
    folded: Optional[Union[bool, Literal["disabled"]]] = None
    loading: Optional[bool] = None
    _removed: Optional[bool] = None


@dataclass
class CapsuleNode(BaseProtocolEntity):
    type: Literal["capsule"] = field(init=False, default="capsule")
    parentId: str = ""
    icon: Optional[str] = None
    title: Optional[str] = None
    target: Optional[Url] = None
    _removed: Optional[bool] = None


@dataclass
class TextNode(BaseProtocolEntity):
    type: Literal["text"] = field(init=False, default="text")
    parentId: str = ""
    operation: Literal["append", "sync"] = "append"
    text: str = ""
    _removed: Optional[bool] = None


ProtocolNode = Union[SectionNode, CapsuleNode, TextNode]


def _emit_upstream(data: ProtocolNode) -> None:
    _get_current_stack().events.append(UpstreamDataEvent(data=data))


@dataclass
class Section(BaseProtocolEntity):
    icon: Optional[str] = None
    title: Optional[str] = None
    folded: Union[bool, Literal["disabled"]] = False
    loading: bool = False
    parentId: Optional[str] = None

    def __post_init__(self) -> None:
        # Ensure timestamp present and emit create
        # Emit create with all provided fields
        payload = SectionNode(
            id=self.id,
            timestamp=self.timestamp,
            parentId=self.parentId,
            icon=self.icon,
            title=self.title,
            folded=self.folded,
            loading=self.loading,
        )
        _emit_upstream(payload)

    def _patch(self, **updates: object) -> None:
        # Only include provided fields in the patch
        patch = SectionNode(id=self.id or "", timestamp=now_ms())
        for key, value in updates.items():
            if hasattr(patch, key):
                setattr(patch, key, value)
        _emit_upstream(patch)

    def append(self, node: Union["Capsule", "Text"]) -> None:
        # Emit create for Capsule when appended; Text does not emit here
        if isinstance(node, Capsule):
            node._emit_create(parent_id=self.id)
        else:
            # Text nodes emit on their own creation (__post_init__) and on append
            pass

    def finish(self) -> None:
        # Stop loading; if it has a title, fold it. If no title, keep folded as disabled
        folded: Union[bool, Literal["disabled"]] = True if self.title else "disabled"
        self._patch(loading=False, folded=folded)

    # Allow direct property-style updates to emit patches via explicit setters
    def set_loading(self, value: bool) -> None:
        self.loading = value
        self._patch(loading=value)

    def set_folded(self, value: Union[bool, Literal["disabled"]]) -> None:
        self.folded = value
        self._patch(folded=value)

    def set_title(self, value: Optional[str]) -> None:
        self.title = value
        self._patch(title=value)

    def remove(self) -> None:
        # Mark this section as removed
        self._patch(_removed=True)


@dataclass
class Capsule:
    parent: Section
    id: str = field(default_factory=gen_id)
    timestamp: float = field(default_factory=now_ms)
    icon: Optional[str] = None
    title: Optional[str] = None
    target: Optional[Url] = None

    def __post_init__(self) -> None:
        self._emit_create(parent_id=self.parent.id)

    def _emit_create(self, parent_id: str) -> None:
        payload = CapsuleNode(
            id=self.id,
            parentId=parent_id,
            timestamp=self.timestamp,
            icon=self.icon,
            title=self.title,
            target=self.target,
        )
        _emit_upstream(payload)

    def remove(self) -> None:
        # Emit a removal update for this capsule
        payload = CapsuleNode(
            id=self.id,
            parentId=self.parent.id,
            timestamp=now_ms(),
            _removed=True,
        )
        _emit_upstream(payload)


@dataclass
class Text:
    parent: Section
    id: str = field(default_factory=gen_id)
    timestamp: float = field(default_factory=now_ms)

    def __post_init__(self) -> None:
        # Emit initial sync to create the Text node with empty content
        _emit_upstream(
            TextNode(
                id=self.id,
                parentId=self.parent.id,
                timestamp=self.timestamp,
                operation="sync",
                text="",
            )
        )

    def append(self, text: str) -> None:
        _emit_upstream(
            TextNode(
                id=self.id,
                parentId=self.parent.id,
                timestamp=now_ms(),
                operation="append",
                text=text,
            )
        )

    def remove(self) -> None:
        # Emit a removal update for this text node
        _emit_upstream(
            TextNode(
                id=self.id,
                parentId=self.parent.id,
                timestamp=now_ms(),
                _removed=True,
            )
        )
