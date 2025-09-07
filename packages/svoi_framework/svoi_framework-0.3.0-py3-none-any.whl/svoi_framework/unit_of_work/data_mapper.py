import abc

from sqlalchemy.orm import DeclarativeBase

from svoi_framework.domain.aggregate import Aggregate


class DataMapper[TAggregate: Aggregate, TModel: DeclarativeBase](abc.ABC):
    @abc.abstractmethod
    def to_orm_model(self, aggregate: TAggregate) -> TModel: ...

    @abc.abstractmethod
    def to_domain(self, orm_model: TModel) -> TAggregate: ...
