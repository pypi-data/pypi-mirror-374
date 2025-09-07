import abc

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase

from svoi_framework.domain import Aggregate
from svoi_framework.unit_of_work import Repository, DataMapper


class SQLAlchemyRepository[TAggregate: Aggregate, TOrmModel: DeclarativeBase](
    Repository[TAggregate], abc.ABC
):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__()
        self._session: AsyncSession = session

    async def add(self, entity: TAggregate) -> None:
        await super().add(entity)
        orm_model = self._mapper.to_orm_model(entity)
        self._session.add(orm_model)

    async def persist(self, entity: TAggregate) -> TAggregate:
        orm_model = self._mapper.to_orm_model(entity)
        merged_model = await self._session.merge(orm_model)
        return self._mapper.to_domain(merged_model)

    @property
    @abc.abstractmethod
    def _mapper(self) -> DataMapper[TAggregate, TOrmModel]: ...
