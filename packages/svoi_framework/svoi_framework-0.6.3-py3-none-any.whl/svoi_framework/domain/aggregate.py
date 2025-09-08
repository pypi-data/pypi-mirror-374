from typing import Protocol, cast


class DomainEvent(Protocol):
    @property
    def type(self) -> str: ...


class Aggregate[TId]:
    def __init__(self, id: TId) -> None:
        self.__id = id
        self.__domain_events: list[DomainEvent] = []

    @property
    def id(self) -> TId:
        return self.__id

    def _push_event(self, event: DomainEvent) -> None:
        self.__domain_events.append(event)

    def collect_events(self) -> list[DomainEvent]:
        events = self.__domain_events
        self.__domain_events = []
        return events

    def __hash__(self) -> int:
        return hash(self.__id)

    def __eq__(self, other: object) -> bool:
        if type(other) is type(self):
            return self.id == cast(Aggregate[TId], other).id
        return False
