import asyncio
import threading

import httpx
import pytest

import use_notify.notification as notification_module
from use_notify import NotificationPublishError, useNotify, useNotifyChannel
from use_notify.notification import Publisher, RetryConfig

from tests.helpers import RecordingChannel, make_http_status_error


class BlockingSyncChannel(RecordingChannel):
    def __init__(self, started_event: threading.Event, release_event: threading.Event):
        super().__init__()
        self.started_event = started_event
        self.release_event = release_event

    def send(self, content, title=None):
        self.started_event.set()
        assert self.release_event.wait(timeout=1)
        super().send(content, title)


class BlockingAsyncChannel(RecordingChannel):
    def __init__(self, started_event: asyncio.Event, release_event: asyncio.Event):
        super().__init__()
        self.started_event = started_event
        self.release_event = release_event

    async def send_async(self, content, title=None):
        self.started_event.set()
        await asyncio.wait_for(self.release_event.wait(), timeout=1)
        await super().send_async(content, title)


def test_publisher_add_and_publish_across_channels():
    first = RecordingChannel()
    second = RecordingChannel()
    publisher = Publisher()

    publisher.add(first, second)
    publisher.publish("hello", title="world")

    assert first.sync_messages == [{"content": "hello", "title": "world"}]
    assert second.sync_messages == [{"content": "hello", "title": "world"}]


@pytest.mark.asyncio
async def test_publisher_publish_async_across_channels():
    first = RecordingChannel()
    second = RecordingChannel()
    publisher = Publisher([first, second])

    await publisher.publish_async("hello", title="world")

    assert first.async_messages == [{"content": "hello", "title": "world"}]
    assert second.async_messages == [{"content": "hello", "title": "world"}]


def test_publisher_retries_retriable_sync_failure():
    channel = RecordingChannel(sync_failures=[TimeoutError("temporary")])
    publisher = Publisher([channel], max_retries=1)

    publisher.publish("hello")

    assert len(channel.sync_messages) == 2


@pytest.mark.asyncio
async def test_publisher_retries_retriable_async_failure():
    channel = RecordingChannel(async_failures=[httpx.ConnectError("boom")])
    publisher = Publisher([channel], max_retries=1)

    await publisher.publish_async("hello")

    assert len(channel.async_messages) == 2


def test_publisher_does_not_retry_non_retriable_failure():
    channel = RecordingChannel(sync_failures=[ValueError("bad config")])
    publisher = Publisher([channel], max_retries=3)

    with pytest.raises(ValueError, match="bad config"):
        publisher.publish("hello")

    assert len(channel.sync_messages) == 1


def test_publisher_retries_http_429_and_eventually_succeeds():
    channel = RecordingChannel(sync_failures=[make_http_status_error(429)])
    publisher = Publisher([channel], max_retries=1)

    publisher.publish("hello")

    assert len(channel.sync_messages) == 2


def test_publisher_aggregates_failures_after_other_channels_continue():
    failing_one = RecordingChannel(sync_failures=[TimeoutError("one"), TimeoutError("one")])
    failing_two = RecordingChannel(sync_failures=[TimeoutError("two"), TimeoutError("two")])
    healthy = RecordingChannel()
    publisher = Publisher([failing_one, healthy, failing_two], max_retries=1)

    with pytest.raises(NotificationPublishError) as error_info:
        publisher.publish("hello")

    assert len(healthy.sync_messages) == 1
    assert len(error_info.value.failures) == 2


def test_publisher_copies_initial_channel_collection():
    initial_channels = [RecordingChannel()]
    publisher = Publisher(initial_channels)

    initial_channels.append(RecordingChannel())
    publisher.publish("hello")

    assert len(publisher.channels) == 1


def test_publisher_add_does_not_affect_in_flight_sync_publish():
    started = threading.Event()
    release = threading.Event()
    first = BlockingSyncChannel(started, release)
    added = RecordingChannel()
    publisher = Publisher([first])
    errors = []

    publish_thread = threading.Thread(
        target=lambda: _publish_and_capture_error(publisher, errors, "hello")
    )
    publish_thread.start()

    assert started.wait(timeout=1)
    publisher.add(added)
    release.set()
    publish_thread.join(timeout=1)

    assert not publish_thread.is_alive()
    assert not errors
    assert len(first.sync_messages) == 1
    assert added.sync_messages == []

    publisher.publish("later")

    assert len(added.sync_messages) == 1


@pytest.mark.asyncio
async def test_publisher_add_does_not_affect_in_flight_async_publish():
    started = asyncio.Event()
    release = asyncio.Event()
    first = BlockingAsyncChannel(started, release)
    added = RecordingChannel()
    publisher = Publisher([first])

    publish_task = asyncio.create_task(publisher.publish_async("hello"))

    await asyncio.wait_for(started.wait(), timeout=1)
    publisher.add(added)
    release.set()
    await asyncio.wait_for(publish_task, timeout=1)

    assert len(first.async_messages) == 1
    assert added.async_messages == []

    await publisher.publish_async("later")

    assert len(added.async_messages) == 1


def test_configure_retry_does_not_affect_in_flight_publish(monkeypatch):
    channel = RecordingChannel(
        sync_failures=[RuntimeError("temporary"), RuntimeError("temporary")]
    )
    publisher = Publisher(
        [channel],
        max_retries=2,
        retry_delay=0.01,
        retriable_exceptions=(RuntimeError,),
    )
    sleep_started = threading.Event()
    release_sleep = threading.Event()
    errors = []

    def controlled_sleep(_delay):
        sleep_started.set()
        assert release_sleep.wait(timeout=1)

    monkeypatch.setattr(notification_module.time, "sleep", controlled_sleep)

    publish_thread = threading.Thread(
        target=lambda: _publish_and_capture_error(publisher, errors, "hello")
    )
    publish_thread.start()

    assert sleep_started.wait(timeout=1)
    publisher.configure_retry(
        max_retries=0,
        retriable_exceptions=(TimeoutError,),
    )
    release_sleep.set()
    publish_thread.join(timeout=1)

    assert not publish_thread.is_alive()
    assert not errors
    assert len(channel.sync_messages) == 3


def test_configure_retry_returns_self_and_updates_policy():
    publisher = Publisher()

    returned = publisher.configure_retry(
        max_retries=2,
        retry_delay=0.5,
        retry_backoff=3.0,
        retriable_exceptions=(RuntimeError,),
    )

    assert returned is publisher
    assert publisher.retry_config == RetryConfig(
        max_retries=2,
        retry_delay=0.5,
        retry_backoff=3.0,
        retriable_exceptions=(RuntimeError,),
    )


def test_retry_config_validates_exception_types():
    with pytest.raises(ValueError, match="exception types"):
        RetryConfig(retriable_exceptions=("invalid",))


def test_notify_from_settings_builds_case_insensitive_channels():
    notify_instance = useNotify.from_settings(
        {
            "bArk": {"token": "bark-token"},
            "wecom": {"token": "wechat-token"},
        }
    )

    assert len(notify_instance.channels) == 2
    assert isinstance(notify_instance.channels[0], useNotifyChannel.Bark)
    assert isinstance(notify_instance.channels[1], useNotifyChannel.WeCom)


def test_notify_from_settings_rejects_unknown_channel():
    with pytest.raises(ValueError, match="Unknown channel"):
        useNotify.from_settings({"unknown": {"token": "x"}})


def _publish_and_capture_error(publisher, errors, content):
    try:
        publisher.publish(content)
    except Exception as error:  # pragma: no cover - exercised via assertions
        errors.append(error)
