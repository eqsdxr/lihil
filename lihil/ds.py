from datetime import datetime, timezone
from typing import ClassVar, dataclass_transform
from uuid import uuid4

from msgspec.json import Decoder

from lihil.interface import Record, field
from lihil.utils.visitor import all_subclasses, union_types


def uuid4_str() -> str:
    return str(uuid4())


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass_transform(frozen_default=True)
class Event(Record, tag_field="typeid", omit_defaults=True):

    # TODO: generate a event page to inspect source
    """
    Description: Identifies the context in which an event happened. Often this will include information such as the type of the event source, the organization publishing the event or the process that produced the event. The exact syntax and semantics behind the data encoded in the URI is defined by the event producer.
    """
    version: ClassVar[str] = "1"


class Envelope[Body: Event](Record, omit_defaults=True):
    """
    a lihil-managed event meta class

    take cloudevents spec as a reference
    https://github.com/cloudevents/spec/blob/main/cloudevents/spec.md

    A container for event, can be used to deliver to kafka, save to pg, etc.
    """

    data: Body

    sub: str = field(default="", name="entity_id")
    source: str = ""
    event_id: str = field(default_factory=uuid4_str)
    timestamp: datetime = field(default_factory=utc_now)

    @classmethod
    def build_decoder(cls) -> Decoder["Envelope[Event]"]:
        event_subs = all_subclasses(Event)
        sub_union = union_types(list(event_subs))
        return Decoder(type=cls[sub_union])  # type: ignoer

    @classmethod
    def from_event(cls, e: Event):
        "reuse metadata such as eventid, source, sub, from event"


# TODO: Command

"""
async def publish(event: Event, subject: str, source: str | None = None):
    eve = Envelope(data=event, subject=subject, source=source)


async def create_user(user: User, bus: EventBus):
    await bus.publish(event = user_created, subject=user.user_id)
"""
