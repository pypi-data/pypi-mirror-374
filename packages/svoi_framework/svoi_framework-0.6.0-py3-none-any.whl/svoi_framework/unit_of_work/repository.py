import abc

from svoi_framework.domain.aggregate import Aggregate, DomainEvent


class Repository[T: Aggregate](abc.ABC):
    def __init__(self) -> None:
        self.__dirty_entities = set[T]()

    async def add(self, entity: T) -> None:
        self.__dirty_entities.add(entity)

    @abc.abstractmethod
    async def persist(self, entity: T) -> T: ...

    def collect_events(self) -> list[DomainEvent]:
        events: list[DomainEvent] = []
        for entity in self.__dirty_entities:
            events.extend(entity.collect_events())

        self.__dirty_entities.clear()
        return events
