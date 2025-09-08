from svoi_framework.domain.aggregate import Aggregate, DomainEvent


class DomainEventTest(DomainEvent):
    @property
    def type(self) -> str:
        return "test"


class AggregateTest(Aggregate[int]):
    def __init__(self, id: int, value: str) -> None:
        super().__init__(id)
        self.value = value

    def action_emit_event(self) -> None:
        self._push_event(DomainEventTest())


def test_aggregate_compared_by_id() -> None:
    # Arrange
    agg = AggregateTest(1, "a")
    same_agg = AggregateTest(1, "b")
    other_agg = AggregateTest(2, "b")

    # Assert
    assert agg == same_agg
    assert agg != other_agg


def test_aggregate_hash_by_id() -> None:
    # Arrange
    agg = AggregateTest(1, "a")
    same_agg = AggregateTest(1, "b")

    # Assert
    assert hash(agg) == hash(same_agg)


def test_aggregate_can_push_events() -> None:
    agg = AggregateTest(1, "a")
    agg.action_emit_event()

    events = agg.collect_events()

    assert len(events) == 1
    assert isinstance(events[0], DomainEventTest)
