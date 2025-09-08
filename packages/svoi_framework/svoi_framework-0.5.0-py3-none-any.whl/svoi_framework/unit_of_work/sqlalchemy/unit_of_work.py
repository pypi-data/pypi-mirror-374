import abc

from sqlalchemy.ext.asyncio import AsyncSession

from svoi_framework.unit_of_work.uow import UnitOfWork, EventPublisher


class SQLAlchemyUnitOfWork(UnitOfWork, abc.ABC):
    def __init__(self, event_dispatcher: EventPublisher, session: AsyncSession) -> None:
        super().__init__(event_dispatcher)
        self.__session = session

    async def commit(self) -> None:
        await super().commit()
        await self.__session.commit()

    async def rollback(self) -> None:
        await super().rollback()
        await self.__session.rollback()

    async def begin(self) -> None:
        await self.__session.begin()

    async def flush(self) -> None:
        await self.__session.flush()
