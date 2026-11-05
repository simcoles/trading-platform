import random

import pytest

from backend.broadcaster import PriceBroadcaster
from backend.pricing import prices


@pytest.fixture
def price_broadcaster():
    return PriceBroadcaster(rng=random.Random(42))


def test_tick_sends_same_prices_to_every_subscriber(price_broadcaster):

    queue1 = price_broadcaster.subscribe()
    queue2 = price_broadcaster.subscribe()

    prices_after_tick = price_broadcaster.tick()
    assert queue1.get_nowait() == prices_after_tick
    assert queue2.get_nowait() == prices_after_tick


def test_slow_subscriber_only_keeps_latest_tick(price_broadcaster):
    queue = price_broadcaster.subscribe()
    price_broadcaster.tick()
    prices_after_second_tick = price_broadcaster.tick()
    assert queue.qsize() == 1
    assert queue.get_nowait() == prices_after_second_tick


def test_unsubscribed_queue_gets_nothing(price_broadcaster):
    queue = price_broadcaster.subscribe()
    price_broadcaster.unsubscribe(queue)
    price_broadcaster.tick()
    assert queue.empty()


def test_tick_does_not_change_shared_prices(price_broadcaster):
    shared_prices_snapshot = dict(prices)
    price_broadcaster.tick()
    price_broadcaster.tick()

    assert prices == shared_prices_snapshot
