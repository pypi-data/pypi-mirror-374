import abc

from svoi_framework.domain.aggregate import DomainEvent
from svoi_framework.unit_of_work import Repository


class EventPublisher(abc.ABC):
    async def dispatch(self, event: DomainEvent) -> None: ...


class UnitOfWork(abc.ABC):
    def __init__(self, event_dispatcher: EventPublisher) -> None:
        self.__event_publisher = event_dispatcher
        self.__repositories: list[Repository] = []

    async def __aenter__(self) -> None:
        await self.begin()

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.rollback()

        if exc_val is not None:
            raise exc_val

    @abc.abstractmethod
    async def commit(self) -> None:
        await self.__dispatch_events()

    @abc.abstractmethod
    async def rollback(self) -> None:
        for repository in self.__repositories:
            _ = repository.collect_events()
        self.__repositories = []

    @abc.abstractmethod
    async def flush(self) -> None: ...

    @abc.abstractmethod
    async def begin(self) -> None: ...

    def _register_repository(self, repository: Repository) -> None:
        self.__repositories.append(repository)

    async def __dispatch_events(self) -> None:
        for repository in self.__repositories:
            events = repository.collect_events()
            for event in events:
                await self.__event_publisher.dispatch(event)
