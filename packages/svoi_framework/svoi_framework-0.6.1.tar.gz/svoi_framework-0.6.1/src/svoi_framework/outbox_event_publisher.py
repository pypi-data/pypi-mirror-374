from typing import Protocol

import sqlalchemy as sa
from opentelemetry.trace import Tracer, Span
from sqlalchemy.ext.asyncio import AsyncSession

from svoi_framework.application.date_time_provider import DateTimeProvider
from svoi_framework.application.uuid_provider import UUIDProvider
from svoi_framework.domain import DomainEvent
from svoi_framework.unit_of_work import EventPublisher


class Handler[T](Protocol):
    async def __call__(self, dispatcher: EventPublisher, event: T) -> None: ...


class Serializer(Protocol):
    def __call__(self, event: DomainEvent) -> str: ...


class TxOutboxEventPublisher(EventPublisher):
    def __init__(
        self,
        session: AsyncSession,
        serializer: Serializer,
        id_provider: UUIDProvider,
        datetime_provider: DateTimeProvider,
        tracer: Tracer,
    ) -> None:
        self._tracer = tracer
        self._datetime_provider = datetime_provider
        self._id_provider = id_provider
        self._serializer = serializer
        self._routes: dict[str, str] = {}
        self._session = session

    async def dispatch(self, event: DomainEvent) -> None:
        target_table = self._routes[event.type]

        query = (
            f"insert into {target_table} (id, type, payload, created_at) "
            "values (:id, :type, :payload, :created_at)"
        )
        params = {
            "id": str(self._id_provider.generate()),
            "type": event.type,
            "payload": self._serializer(event),
            "created_at": self._datetime_provider.utc_now(),
        }
        await self._session.execute(sa.text(query), params)

    def route(self, event_type: str, target_table: str) -> None:
        self._routes[event_type] = target_table
