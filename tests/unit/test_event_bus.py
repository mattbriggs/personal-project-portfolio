"""Unit tests for the EventBus."""

from portfolio_manager.events.event_bus import EventBus


class TestEventBus:
    def test_subscribe_and_emit(self):
        bus = EventBus.get()
        received = []
        bus.subscribe("TEST_EVENT", lambda **kw: received.append(kw))
        bus.emit("TEST_EVENT", value=42)
        assert received == [{"value": 42}]

    def test_emit_unknown_event_is_no_op(self):
        bus = EventBus.get()
        # Should not raise
        bus.emit("NO_SUBSCRIBERS_EVENT")

    def test_unsubscribe_stops_delivery(self):
        bus = EventBus.get()
        received = []

        def cb(**kw):
            received.append(kw)

        bus.subscribe("TEST_UNSUB", cb)
        bus.unsubscribe("TEST_UNSUB", cb)
        bus.emit("TEST_UNSUB", x=1)
        assert received == []

    def test_unsubscribe_missing_is_no_op(self):
        bus = EventBus.get()
        # Should not raise
        bus.unsubscribe("NEVER_SUBSCRIBED", lambda **kw: None)

    def test_subscriber_exception_does_not_block_others(self):
        bus = EventBus.get()
        received = []

        def bad_cb(**kw):
            raise RuntimeError("intentional failure")

        def good_cb(**kw):
            received.append(kw)

        bus.subscribe("MULTI", bad_cb)
        bus.subscribe("MULTI", good_cb)
        bus.emit("MULTI", x=99)
        assert received == [{"x": 99}]

    def test_get_creates_singleton(self):
        a = EventBus.get()
        b = EventBus.get()
        assert a is b

    def test_reset_creates_fresh_instance(self):
        a = EventBus.get()
        EventBus.reset()
        b = EventBus.get()
        assert a is not b
