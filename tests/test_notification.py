import httpx
import pytest

from use_notify import NotificationPublishError, useNotify, useNotifyChannel
from use_notify.notification import Publisher, RetryConfig

from tests.helpers import RecordingChannel, make_http_status_error


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
