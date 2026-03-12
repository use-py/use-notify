import asyncio
from concurrent.futures import ThreadPoolExecutor
import threading

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

    def test_default_instance_is_resolved_at_call_time(self):
        channel = RecordingChannel()

        @notify()
        def task():
            return "ok"

        set_default_notify_instance(useNotify([channel]))

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

    def test_default_instance_is_isolated_per_thread(self):
        first_channel = RecordingChannel()
        second_channel = RecordingChannel()
        barrier = threading.Barrier(2)

        @notify()
        def task():
            return "ok"

        def worker(channel):
            set_default_notify_instance(useNotify([channel]))
            barrier.wait()
            try:
                return task()
            finally:
                clear_default_notify_instance()

        with ThreadPoolExecutor(max_workers=2) as executor:
            first_result = executor.submit(worker, first_channel)
            second_result = executor.submit(worker, second_channel)

        assert first_result.result() == "ok"
        assert second_result.result() == "ok"
        assert len(first_channel.sync_messages) == 1
        assert len(second_channel.sync_messages) == 1

    @pytest.mark.asyncio
    async def test_default_instance_is_isolated_per_async_task(self):
        first_channel = RecordingChannel()
        second_channel = RecordingChannel()

        @notify(include_result=True)
        async def task(label):
            await asyncio.sleep(0)
            return label

        async def worker(label, channel):
            set_default_notify_instance(useNotify([channel]))
            try:
                return await task(label)
            finally:
                clear_default_notify_instance()

        first_result, second_result = await asyncio.gather(
            worker("first", first_channel),
            worker("second", second_channel),
        )

        assert first_result == "first"
        assert second_result == "second"
        assert len(first_channel.async_messages) == 1
        assert len(second_channel.async_messages) == 1
        assert "first" in first_channel.async_messages[0]["content"]
        assert "second" in second_channel.async_messages[0]["content"]

    def test_sync_timeout_does_not_block_main_thread(self):
        """测试同步超时不阻塞主线程"""
        import time

        class SlowChannel(RecordingChannel):
            def send(self, content, title=None):
                time.sleep(2)
                super().send(content, title)

        channel = SlowChannel()
        notify_instance = useNotify([channel])

        @notify(notify_instance=notify_instance, timeout=0.1)
        def task():
            return "ok"

        start = time.time()
        result = task()
        elapsed = time.time() - start

        # 函数应该立即返回，不等待2秒
        assert result == "ok"
        assert elapsed < 0.5, f"函数执行时间 {elapsed:.2f}s 超过预期"
        # 超时错误应该被记录（不抛出，避免影响原函数执行）

    @pytest.mark.asyncio
    async def test_sync_timeout_in_async_event_loop(self):
        """测试同步超时在异步事件循环中也能正确应用"""
        import time

        class SlowChannel(RecordingChannel):
            def send(self, content, title=None):
                time.sleep(2)
                super().send(content, title)

        channel = SlowChannel()
        notify_instance = useNotify([channel])

        @notify(notify_instance=notify_instance, timeout=0.1)
        def sync_task():
            return "ok"

        import asyncio
        start = asyncio.get_event_loop().time()

        # 在异步上下文中调用同步装饰器
        result = sync_task()

        elapsed = asyncio.get_event_loop().time() - start

        # 函数应该立即返回，不等待2秒
        assert result == "ok"
        assert elapsed < 0.5, f"函数执行时间 {elapsed:.2f}s 超过预期"

    def test_sync_send_without_timeout(self):
        """测试不设置超时时正常发送"""
        channel = RecordingChannel()
        notify_instance = useNotify([channel])

        @notify(notify_instance=notify_instance)
        def task():
            return "ok"

        result = task()
        assert result == "ok"
        assert len(channel.sync_messages) == 1

    @pytest.mark.asyncio
    async def test_async_timeout_works(self):
        """测试异步超时正常工作"""
        class SlowChannel(RecordingChannel):
            async def send_async(self, content, title=None):
                await asyncio.sleep(2)
                await super().send_async(content, title)

        channel = SlowChannel()
        notify_instance = useNotify([channel])

        @notify(notify_instance=notify_instance, timeout=0.1, notify_on_error=False)
        async def task():
            return "ok"

        start = asyncio.get_event_loop().time()
        result = await task()
        elapsed = asyncio.get_event_loop().time() - start

        # 函数应该立即返回，不等待2秒
        assert result == "ok"
        assert elapsed < 0.5, f"函数执行时间 {elapsed:.2f}s 超过预期"
        # 超时应该生效，通知发送失败
        assert len(channel.async_messages) == 0


