import abc
from typing import Any

from dishka import AsyncContainer


class QueryDispatcher(abc.ABC):

    @abc.abstractmethod
    async def query(self, query: Any) -> Any: ...


class QueryHandler(abc.ABC):
    @abc.abstractmethod
    async def handle(self, query: Any) -> Any: ...


class DefaultQueryDispatcher(QueryDispatcher):

    def __init__(self, container: AsyncContainer) -> None:
        self.__container = container
        self.__query_handlers: dict[type[Any], type[Any]] = {}

    async def query(self, query: Any) -> Any:
        handler_type = self.__query_handlers[type(query)]
        handler = await self.__container.get(handler_type)
        return await handler.handle(query)

    def add_query_handler(self, query_type: type[Any], query_handler_type: type[QueryHandler]) -> None:
        assert query_handler_type not in self.__query_handlers
        self.__query_handlers[query_type] = query_handler_type
