import asyncio
import smtplib
import threading

import httpx
import pytest

import use_notify.notification as notification_module
from tests.helpers import RecordingChannel, make_http_status_error
from use_notify import NotificationPublishError, useNotify, useNotifyChannel
from use_notify.notification import Publisher, RetryConfig
from use_notify.redaction import redact_text


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


def test_publisher_add_without_channels_is_noop():
    first = RecordingChannel()
    publisher = Publisher([first])

    publisher.add()
    publisher.publish("hello")

    assert publisher.channels == (first,)
    assert first.sync_messages == [{"content": "hello", "title": None}]


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


def test_retry_config_normalizes_retriable_exception_list():
    retry_config = RetryConfig(retriable_exceptions=[RuntimeError])

    assert retry_config.retriable_exceptions == (RuntimeError,)


def test_publisher_retries_retriable_exception_list():
    channel = RecordingChannel(sync_failures=[RuntimeError("temporary")])
    publisher = Publisher([channel], max_retries=1, retriable_exceptions=[RuntimeError])

    publisher.publish("hello")

    assert len(channel.sync_messages) == 2


@pytest.mark.asyncio
async def test_publisher_retries_async_retriable_exception_list():
    channel = RecordingChannel(async_failures=[RuntimeError("temporary")])
    publisher = Publisher([channel], max_retries=1, retriable_exceptions=[RuntimeError])

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


def test_publisher_does_not_retry_http_400():
    channel = RecordingChannel(sync_failures=[make_http_status_error(400)])
    publisher = Publisher([channel], max_retries=3)

    with pytest.raises(httpx.HTTPStatusError, match="status 400"):
        publisher.publish("hello")

    assert len(channel.sync_messages) == 1


def test_publisher_classifies_provider_specific_retry_exceptions():
    publisher = Publisher()

    assert publisher._is_retriable_exception(make_http_status_error(408), publisher.retry_config)
    assert publisher._is_retriable_exception(httpx.ConnectError("network"), publisher.retry_config)
    assert publisher._is_retriable_exception(
        smtplib.SMTPResponseException(450, b"mailbox unavailable"),
        publisher.retry_config,
    )
    assert not publisher._is_retriable_exception(
        smtplib.SMTPAuthenticationError(535, b"auth failed"),
        publisher.retry_config,
    )
    assert not publisher._is_retriable_exception(
        smtplib.SMTPResponseException(550, b"mailbox unavailable"),
        publisher.retry_config,
    )


def test_publisher_aggregates_failures_after_other_channels_continue():
    failing_one = RecordingChannel(sync_failures=[TimeoutError("one"), TimeoutError("one")])
    failing_two = RecordingChannel(sync_failures=[TimeoutError("two"), TimeoutError("two")])
    healthy = RecordingChannel()
    publisher = Publisher([failing_one, healthy, failing_two], max_retries=1)

    with pytest.raises(NotificationPublishError) as error_info:
        publisher.publish("hello")

    assert len(healthy.sync_messages) == 1
    assert len(error_info.value.failures) == 2


@pytest.mark.asyncio
async def test_publisher_aggregates_async_failures_after_other_channels_continue():
    failing_one = RecordingChannel(async_failures=[httpx.ConnectError("one")])
    failing_two = RecordingChannel(async_failures=[httpx.ConnectError("two")])
    healthy = RecordingChannel()
    publisher = Publisher([failing_one, healthy, failing_two])

    with pytest.raises(NotificationPublishError) as error_info:
        await publisher.publish_async("hello")

    assert len(healthy.async_messages) == 1
    assert len(error_info.value.failures) == 2


def test_single_channel_failure_redacts_secret_from_exception_message():
    request = httpx.Request(
        "POST",
        "https://oapi.dingtalk.com/robot/send?access_token=ding-secret-token",
    )
    response = httpx.Response(500, request=request)
    channel_error = httpx.HTTPStatusError(
        "request failed for " "https://oapi.dingtalk.com/robot/send?access_token=ding-secret-token",
        request=request,
        response=response,
    )
    channel = RecordingChannel(sync_failures=[channel_error])
    publisher = Publisher([channel])

    with pytest.raises(httpx.HTTPStatusError) as error_info:
        publisher.publish("hello")

    message = str(error_info.value)
    assert "ding-secret-token" not in message
    assert "access_token=<redacted>" in message


def test_aggregate_failure_redacts_secrets_from_exception_message():
    failing_one = RecordingChannel(
        sync_failures=[RuntimeError("failed https://api.day.app/bark-secret-token")]
    )
    failing_two = RecordingChannel(
        sync_failures=[
            RuntimeError(
                "failed https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=wechat-secret-token"
            )
        ]
    )
    publisher = Publisher([failing_one, failing_two])

    with pytest.raises(NotificationPublishError) as error_info:
        publisher.publish("hello")

    message = str(error_info.value)
    assert "bark-secret-token" not in message
    assert "wechat-secret-token" not in message
    assert "<redacted>" in message


def test_redacts_custom_base_url_path_secrets():
    message = (
        "failed https://bark.example.com/bark-secret-token "
        "and https://ntfy.example.com/my-secret-topic"
        " and https://notify.example.com/abc123def456ghi7"
    )

    redacted = redact_text(message)

    assert "bark-secret-token" not in redacted
    assert "my-secret-topic" not in redacted
    assert "abc123def456ghi7" not in redacted
    assert "https://bark.example.com/<redacted>" in redacted
    assert "https://ntfy.example.com/<redacted>" in redacted
    assert "https://notify.example.com/<redacted>" in redacted


def test_redaction_keeps_multi_segment_urls_visible():
    message = "docs https://example.com/path/to/page"

    assert redact_text(message) == message


def test_redaction_keeps_ordinary_single_segment_urls_visible():
    message = (
        "docs https://example.com/docs "
        "and status https://status.example.com/health "
        "and keyboard https://example.com/keyboard"
    )

    assert redact_text(message) == message


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
    channel = RecordingChannel(sync_failures=[RuntimeError("temporary"), RuntimeError("temporary")])
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

    with pytest.raises(ValueError, match="exception types"):
        RetryConfig(retriable_exceptions=RuntimeError)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"max_retries": True},
        {"retry_delay": False},
        {"retry_backoff": True},
    ],
)
def test_retry_config_rejects_bool_numeric_values(kwargs):
    with pytest.raises(ValueError):
        RetryConfig(**kwargs)


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
