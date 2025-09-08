import abc
from typing import Protocol, cast

from dishka import AsyncContainer


class BaseCommand:
    pass


class Command[TResult](BaseCommand):
    pass


class Event:
    pass


class EventDispatcher(abc.ABC):
    @abc.abstractmethod
    async def execute_command(self, command: BaseCommand) -> None: ...

    @abc.abstractmethod
    async def dispatch_event(self, event: Event) -> None: ...


class EventHandler(abc.ABC):
    @abc.abstractmethod
    async def handle(self, event: Event) -> None: ...


class CommandHandler[TResult](abc.ABC):
    @abc.abstractmethod
    async def handle(self, command: Command[TResult]) -> TResult: ...


class DefaultEventDispatcher(EventDispatcher):
    def __init__(self, container: AsyncContainer) -> None:
        self.__container = container
        self.__event_handlers: dict[type[Event], list[type[EventHandler]]] = {}
        self.__command_handlers: dict[type[BaseCommand], type[CommandHandler]] = {}

    async def dispatch_event(self, event: Event) -> None:
        handler_types = self.__event_handlers.get(type(event))
        if handler_types is None:
            return
        for handler_type in handler_types:
            handler: EventHandler | None = await self.__container.get(handler_type)
            assert handler is not None
            await handler.handle(event)

    def add_event_handler[TEvent: Event, THandler: EventHandler](
        self, event_type: type[TEvent], handler: type[THandler]
    ) -> None:
        if event_type not in self.__event_handlers:
            self.__event_handlers[event_type] = []

        self.__event_handlers[event_type].append(handler)

    def add_command_handler[TCommand: Command, TResult](
        self, command_type: type[TCommand], handler: type[CommandHandler[TResult]]
    ) -> None:
        if command_type in self.__command_handlers:
            raise TypeError(f"Command type {command_type} already registered")

        self.__command_handlers[command_type] = handler

    async def execute_command[TResult](self, command: BaseCommand) -> TResult:
        handler_type = self.__command_handlers[type(command)]
        handler = await self.__container.get(handler_type)
        assert handler is not None
        result = await handler.handle(cast(Command[TResult], command))
        return cast(TResult, result)
