import asyncio

import pytest

from use_notify import (
    clear_default_notify_instance,
    get_default_notify_instance,
    notify,
    set_default_notify_instance,
    useNotify,
)
from use_notify.decorator import NotifyConfigError, NotifyDecorator

from tests.helpers import RecordingChannel


class TestNotifyDecorator:
    def teardown_method(self):
        clear_default_notify_instance()

    def test_sync_success_sends_notification(self):
        channel = RecordingChannel()
        notify_instance = useNotify([channel])

        @notify(notify_instance=notify_instance, title="任务通知")
        def task():
            return {"status": "ok"}

        result = task()

        assert result == {"status": "ok"}
        assert channel.sync_messages[0]["title"] == "任务通知"
        assert "执行成功" in channel.sync_messages[0]["content"]

    def test_sync_error_sends_notification_and_reraises(self):
        channel = RecordingChannel()
        notify_instance = useNotify([channel])

        @notify(notify_instance=notify_instance)
        def task():
            raise RuntimeError("boom")

        with pytest.raises(RuntimeError, match="boom"):
            task()

        assert "执行失败" in channel.sync_messages[0]["content"]
        assert "boom" in channel.sync_messages[0]["content"]

    @pytest.mark.asyncio
    async def test_async_success_sends_notification(self):
        channel = RecordingChannel()
        notify_instance = useNotify([channel])

        @notify(notify_instance=notify_instance, include_result=True)
        async def task():
            await asyncio.sleep(0)
            return "async-ok"

        result = await task()

        assert result == "async-ok"
        assert "async-ok" in channel.async_messages[0]["content"]

    def test_uses_default_notify_instance(self):
        channel = RecordingChannel()
        default_notify = useNotify([channel])
        set_default_notify_instance(default_notify)

        @notify()
        def task():
            return "ok"

        assert get_default_notify_instance() is default_notify
        assert task() == "ok"
        assert len(channel.sync_messages) == 1

    def test_explicit_instance_overrides_default(self):
        default_channel = RecordingChannel()
        explicit_channel = RecordingChannel()
        set_default_notify_instance(useNotify([default_channel]))

        @notify(notify_instance=useNotify([explicit_channel]))
        def task():
            return "ok"

        task()

        assert len(default_channel.sync_messages) == 0
        assert len(explicit_channel.sync_messages) == 1

    def test_retry_overrides_apply_without_mutating_source_notify(self):
        channel = RecordingChannel(sync_failures=[TimeoutError("temporary")])
        base_notify = useNotify([channel])

        @notify(notify_instance=base_notify, max_retries=1)
        def task():
            return "ok"

        assert task() == "ok"
        assert len(channel.sync_messages) == 2
        assert base_notify.retry_config.max_retries == 0

    def test_invalid_retry_configuration_is_rejected(self):
        with pytest.raises(NotifyConfigError):
            NotifyDecorator(max_retries=-1)

        with pytest.raises(NotifyConfigError):
            NotifyDecorator(retriable_exceptions=["bad"])

    def test_notification_failures_do_not_break_wrapped_function(self):
        channel = RecordingChannel(sync_failures=[ValueError("broken sender")])
        notify_instance = useNotify([channel])

        @notify(notify_instance=notify_instance)
        def task():
            return "business-result"

        assert task() == "business-result"
        assert len(channel.sync_messages) == 1
