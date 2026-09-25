import pytest

from demo.ratelimit import TokenBucket


class FakeClock:
    def __init__(self) -> None:
        self.now = 0.0

    def __call__(self) -> float:
        return self.now


def test_burst_then_refill() -> None:
    clock = FakeClock()
    bucket = TokenBucket(capacity=2, rate=1.0, clock=clock)
    assert bucket.allow()
    assert bucket.allow()
    assert not bucket.allow()
    clock.now = 1.0
    assert bucket.allow()
    assert not bucket.allow()


def test_refill_never_exceeds_capacity() -> None:
    clock = FakeClock()
    bucket = TokenBucket(capacity=3, rate=10.0, clock=clock)
    clock.now = 100.0
    assert all(bucket.allow() for _ in range(3))
    assert not bucket.allow()


@pytest.mark.parametrize("kwargs", [{"capacity": 0, "rate": 1.0}, {"capacity": 1, "rate": 0.0}])
def test_rejects_invalid_configuration(kwargs: dict) -> None:
    with pytest.raises(ValueError):
        TokenBucket(**kwargs)
