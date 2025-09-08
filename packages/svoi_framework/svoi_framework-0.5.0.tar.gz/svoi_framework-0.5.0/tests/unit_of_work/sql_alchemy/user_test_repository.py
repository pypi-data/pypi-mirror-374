import uuid
from dataclasses import dataclass
from typing import cast

from sqlalchemy import String
import sqlalchemy as sql
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from svoi_framework.domain.aggregate import Aggregate, DomainEvent
from svoi_framework.unit_of_work import DataMapper, EventPublisher
from svoi_framework.unit_of_work.sqlalchemy import (
    SQLAlchemyRepository,
    SQLAlchemyUnitOfWork,
)


class Base(DeclarativeBase):
    pass


@dataclass(frozen=True, eq=True)
class UserTestEvent(DomainEvent):
    @property
    def type(self) -> str:
        return "test"

    value: str


class UserTestAggregate(Aggregate[uuid.UUID]):
    def __init__(self, user_id: uuid.UUID, first_name: str, last_name: str) -> None:
        super().__init__(user_id)
        self.first_name = first_name
        self.last_name = last_name

    def add_event(self, value: str) -> None:
        self._push_event(UserTestEvent(value))


class UserTestOrmModel(Base):
    __tablename__ = "users"

    user_id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(30), nullable=False)
    last_name: Mapped[str] = mapped_column(String(30), nullable=False)


class UserTestDataMapper(DataMapper[UserTestAggregate, UserTestOrmModel]):
    def to_orm_model(self, aggregate: UserTestAggregate) -> UserTestOrmModel:
        return UserTestOrmModel(
            user_id=aggregate.id,
            first_name=aggregate.first_name,
            last_name=aggregate.last_name,
        )

    def to_domain(self, orm_model: UserTestOrmModel) -> UserTestAggregate:
        return UserTestAggregate(
            user_id=orm_model.user_id,
            first_name=orm_model.first_name,
            last_name=orm_model.last_name,
        )


class UserTestRepository(SQLAlchemyRepository[UserTestAggregate, UserTestOrmModel]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    @property
    def _mapper(self) -> DataMapper[UserTestAggregate, UserTestOrmModel]:
        return UserTestDataMapper()

    async def get_by_id(self, user_id: uuid.UUID) -> UserTestOrmModel:
        query = sql.select(UserTestOrmModel).where(UserTestOrmModel.user_id == user_id)
        result = await self._session.scalars(query)
        return cast(UserTestOrmModel, result.first())


class SqlAlchemyTestUnitOfWork(SQLAlchemyUnitOfWork):
    def __init__(
        self,
        event_dispatcher: EventPublisher,
        session: AsyncSession,
    ) -> None:
        super().__init__(event_dispatcher, session)
        self.user_repository = UserTestRepository(session)
        self._register_repository(self.user_repository)
