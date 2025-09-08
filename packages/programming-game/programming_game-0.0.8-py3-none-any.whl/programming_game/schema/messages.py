from collections.abc import Mapping

from msgspec import Struct

from .events import AnyEvent


class VersionMessage(Struct, tag="version"):
    value: str


class EventsMessage(Struct, tag="events"):
    value: Mapping[str, Mapping[str, list[AnyEvent]]]


ServerMessage = VersionMessage | EventsMessage
