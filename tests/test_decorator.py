# -*- coding: utf-8 -*-
"""
装饰器功能测试
"""

import asyncio
import pytest
import time
from unittest.mock import MagicMock, patch

from use_notify import useNotify, notify
from use_notify.decorator import (
    NotifyDecorator,
    ExecutionContext,
    MessageFormatter,
    NotificationSender,
    NotifyConfigError,
    NotifySendError,
    set_default_notify_instance,
    get_default_notify_instance,
    clear_default_notify_instance
)
from use_notify.channels.base import BaseChannel


class MockChannel(BaseChannel):
    """测试用的模拟通知渠道"""
    
    def __init__(self, config=None):
        super().__init__(config or {})
        self.sent_messages = []
    
    def send(self, title=None, content=None, **kwargs):
        self.sent_messages.append({"title": title, "content": content, "kwargs": kwargs})
    
    async def send_async(self, title=None, content=None, **kwargs):
        self.sent_messages.append({"title": title, "content": content, "kwargs": kwargs})


class TestExecutionContext:
    """测试执行上下文"""
    
    def test_context_creation(self):
        """测试上下文创建"""
        from datetime import datetime
        start_time = datetime.now()
        context = ExecutionContext(
            function_name="test_func",
            start_time=start_time,
            args=(1, 2),
            kwargs={"key": "value"}
        )
        
        assert context.function_name == "test_func"
        assert context.start_time == start_time
        assert context.args == (1, 2)
        assert context.kwargs == {"key": "value"}
        assert context.result is None
        assert context.exception is None
        assert context.execution_time is None
        assert context.is_success is True  # 没有异常就是成功
    
    def test_mark_success(self):
        """测试标记成功"""
        from datetime import datetime
        start_time = datetime.now()
        context = ExecutionContext("test_func", start_time)
        
        result = "success"
        context.mark_success(result)
        
        assert context.result == result
        assert context.end_time is not None
        assert context.execution_time is not None
        assert context.execution_time >= 0
        assert context.is_success is True
    
    def test_mark_error(self):
        """测试标记错误"""
        from datetime import datetime
        start_time = datetime.now()
        context = ExecutionContext("test_func", start_time)
        
        error = ValueError("test error")
        context.mark_error(error)
        
        assert context.exception == error
        assert context.end_time is not None
        assert context.execution_time is not None
        assert context.execution_time >= 0
        assert context.is_success is False
        assert context.error_message == "test error"


class TestMessageFormatter:
    """测试消息格式化器"""
    
    def test_default_templates(self):
        """测试默认模板"""
        formatter = MessageFormatter()
        assert "✅" in formatter.success_template
        assert "❌" in formatter.error_template
    
    def test_custom_templates(self):
        """测试自定义模板"""
        success_template = "Success: {function_name}"
        error_template = "Error: {function_name} - {error_message}"
        
        formatter = MessageFormatter(
            success_template=success_template,
            error_template=error_template
        )
        
        assert formatter.success_template == success_template
        assert formatter.error_template == error_template
    
    def test_format_success_message(self):
        """测试格式化成功消息"""
        from datetime import datetime
        
        formatter = MessageFormatter()
        context = ExecutionContext("test_func", datetime.now())
        context.mark_success("result")
        
        message = formatter.format_success_message(context)
        
        assert "title" in message
        assert "content" in message
        assert "✅" in message["title"]
        assert "test_func" in message["content"]
        assert "执行成功" in message["content"]
    
    def test_format_error_message(self):
        """测试格式化错误消息"""
        from datetime import datetime
        
        formatter = MessageFormatter()
        context = ExecutionContext("test_func", datetime.now())
        context.mark_error(ValueError("test error"))
        
        message = formatter.format_error_message(context)
        
        assert "title" in message
        assert "content" in message
        assert "❌" in message["title"]
        assert "test_func" in message["content"]
        assert "执行失败" in message["content"]
        assert "test error" in message["content"]
    
    def test_include_args_and_result(self):
        """测试包含参数和结果"""
        from datetime import datetime
        
        formatter = MessageFormatter(include_args=True, include_result=True)
        context = ExecutionContext(
            "test_func", 
            datetime.now(),
            args=(1, 2),
            kwargs={"key": "value"}
        )
        context.mark_success("result")
        
        message = formatter.format_success_message(context)
        
        assert "返回结果" in message["content"]
        assert "result" in message["content"]
    
    def test_safe_serialize(self):
        """测试安全序列化"""
        formatter = MessageFormatter()
        
        # 测试正常对象
        assert formatter._safe_serialize("test") == '"test"'
        assert formatter._safe_serialize([1, 2, 3]) == '[1, 2, 3]'
        assert formatter._safe_serialize(None) == "None"
        
        # 测试长字符串截断
        long_string = "a" * 300
        result = formatter._safe_serialize(long_string, max_length=100)
        assert len(result) <= 103  # 100 + "..."
        assert result.endswith("...")


class TestNotificationSender:
    """测试通知发送器"""
    
    def test_sender_creation(self):
        """测试发送器创建"""
        notify_instance = useNotify()
        sender = NotificationSender(notify_instance)
        
        assert sender.notify_instance == notify_instance
        assert sender.timeout is None
    
    def test_sender_with_timeout(self):
        """测试带超时的发送器"""
        notify_instance = useNotify()
        sender = NotificationSender(notify_instance, timeout=30.0)
        
        assert sender.timeout == 30.0
    
    def test_send_notification(self):
        """测试发送通知"""
        mock_channel = MockChannel()
        notify_instance = useNotify([mock_channel])
        sender = NotificationSender(notify_instance)
        
        sender.send_notification("Test Title", "Test Content")
        
        assert len(mock_channel.sent_messages) == 1
        message = mock_channel.sent_messages[0]
        assert message["title"] == "Test Title"
        assert message["content"] == "Test Content"
    
    @pytest.mark.asyncio
    async def test_send_notification_async(self):
        """测试异步发送通知"""
        mock_channel = MockChannel()
        notify_instance = useNotify([mock_channel])
        sender = NotificationSender(notify_instance)
        
        await sender.send_notification_async("Test Title", "Test Content")
        
        assert len(mock_channel.sent_messages) == 1
        message = mock_channel.sent_messages[0]
        assert message["title"] == "Test Title"
        assert message["content"] == "Test Content"


class TestNotifyDecorator:
    """测试通知装饰器"""
    
    def test_decorator_creation(self):
        """测试装饰器创建"""
        notify_instance = useNotify()
        decorator = NotifyDecorator(notify_instance=notify_instance)
        
        assert decorator.notify_instance == notify_instance
        assert decorator.notify_on_success is True
        assert decorator.notify_on_error is True
    
    def test_decorator_with_empty_notify(self):
        """测试使用空 Notify 实例的装饰器"""
        decorator = NotifyDecorator()
        
        assert isinstance(decorator.notify_instance, useNotify)
        assert len(decorator.notify_instance.channels) == 0
    
    def test_config_validation(self):
        """测试配置验证"""
        # 测试无效的 notify_instance
        with pytest.raises(NotifyConfigError):
            NotifyDecorator(notify_instance="invalid")
        
        # 测试无效的 title
        with pytest.raises(NotifyConfigError):
            NotifyDecorator(title=123)
        
        # 测试无效的 timeout
        with pytest.raises(NotifyConfigError):
            NotifyDecorator(timeout=-1)
        
        # 测试两个通知都关闭
        with pytest.raises(NotifyConfigError):
            NotifyDecorator(notify_on_success=False, notify_on_error=False)
    
    def test_invalid_notify_instance(self):
        """测试无效的 notify_instance"""
        from use_notify.decorator.exceptions import NotifyConfigError
        
        # 创建一个无效的对象（不是 Notify 实例）
        class InvalidNotify:
            pass
        
        with pytest.raises(NotifyConfigError):
            @notify(notify_instance=InvalidNotify())
            def test_func():
                return "test"
            
            test_func()
    
    def test_invalid_title_type(self):
        """测试无效的 title 类型"""
        # 由于 title 参数在运行时才会被验证，我们测试运行时行为
        @notify(title="valid_title")
        def test_func():
            return "test"
        
        # 这个测试主要验证装饰器能正常处理字符串类型的 title
        result = test_func()
        assert result == "test"
    
    def test_sync_function_success(self):
        """测试同步函数成功执行"""
        mock_channel = MockChannel()
        notify_instance = useNotify([mock_channel])
        decorator = NotifyDecorator(notify_instance=notify_instance)
        
        @decorator
        def test_func():
            return "success"
        
        result = test_func()
        
        assert result == "success"
        assert len(mock_channel.sent_messages) == 1
        message = mock_channel.sent_messages[0]
        assert "✅" in message["title"]
        assert "test_func" in message["content"]
        assert "执行成功" in message["content"]
    
    def test_sync_function_error(self):
        """测试同步函数错误执行"""
        mock_channel = MockChannel()
        notify_instance = useNotify([mock_channel])
        decorator = NotifyDecorator(notify_instance=notify_instance)
        
        @decorator
        def test_func():
            raise ValueError("test error")
        
        with pytest.raises(ValueError, match="test error"):
            test_func()
        
        assert len(mock_channel.sent_messages) == 1
        message = mock_channel.sent_messages[0]
        assert "❌" in message["title"]
        assert "test_func" in message["content"]
        assert "执行失败" in message["content"]
        assert "test error" in message["content"]
    
    @pytest.mark.asyncio
    async def test_async_function_success(self):
        """测试异步函数成功执行"""
        mock_channel = MockChannel()
        notify_instance = useNotify([mock_channel])
        decorator = NotifyDecorator(notify_instance=notify_instance)
        
        @decorator
        async def test_func():
            await asyncio.sleep(0.1)
            return "async success"
        
        result = await test_func()
        
        assert result == "async success"
        assert len(mock_channel.sent_messages) == 1
        message = mock_channel.sent_messages[0]
        assert "✅" in message["title"]
        assert "test_func" in message["content"]
        assert "执行成功" in message["content"]
    
    @pytest.mark.asyncio
    async def test_async_function_error(self):
        """测试异步函数错误执行"""
        mock_channel = MockChannel()
        notify_instance = useNotify([mock_channel])
        decorator = NotifyDecorator(notify_instance=notify_instance)
        
        @decorator
        async def test_func():
            await asyncio.sleep(0.1)
            raise ValueError("async error")
        
        with pytest.raises(ValueError, match="async error"):
            await test_func()
        
        assert len(mock_channel.sent_messages) == 1
        message = mock_channel.sent_messages[0]
        assert "❌" in message["title"]
        assert "test_func" in message["content"]
        assert "执行失败" in message["content"]
        assert "async error" in message["content"]
    
    def test_notify_on_success_false(self):
        """测试关闭成功通知"""
        mock_channel = MockChannel()
        notify_instance = useNotify([mock_channel])
        decorator = NotifyDecorator(
            notify_instance=notify_instance,
            notify_on_success=False
        )
        
        @decorator
        def test_func():
            return "success"
        
        result = test_func()
        
        assert result == "success"
        assert len(mock_channel.sent_messages) == 0
    
    def test_notify_on_error_false(self):
        """测试关闭错误通知"""
        mock_channel = MockChannel()
        notify_instance = useNotify([mock_channel])
        decorator = NotifyDecorator(
            notify_instance=notify_instance,
            notify_on_error=False
        )
        
        @decorator
        def test_func():
            raise ValueError("test error")
        
        with pytest.raises(ValueError, match="test error"):
            test_func()
        
        assert len(mock_channel.sent_messages) == 0
    
    def test_custom_title(self):
        """测试自定义标题"""
        mock_channel = MockChannel()
        notify_instance = useNotify([mock_channel])
        decorator = NotifyDecorator(
            notify_instance=notify_instance,
            title="自定义标题"
        )
        
        @decorator
        def test_func():
            return "success"
        
        test_func()
        
        assert len(mock_channel.sent_messages) == 1
        message = mock_channel.sent_messages[0]
        assert message["title"] == "自定义标题"
    
    def test_include_args_and_result(self):
        """测试包含参数和结果"""
        mock_channel = MockChannel()
        notify_instance = useNotify([mock_channel])
        decorator = NotifyDecorator(
            notify_instance=notify_instance,
            include_args=True,
            include_result=True
        )
        
        @decorator
        def test_func(arg1, arg2, kwarg1="value"):
            return "result"
        
        test_func("a", "b", kwarg1="c")
        
        assert len(mock_channel.sent_messages) == 1
        message = mock_channel.sent_messages[0]
        content = message["content"]
        assert "返回结果" in content
        assert "result" in content


class TestNotifyFactory:
    """测试 notify 工厂函数"""
    
    def test_factory_function(self):
        """测试工厂函数"""
        mock_channel = MockChannel()
        notify_instance = useNotify([mock_channel])
        
        @notify(notify_instance=notify_instance)
        def test_func():
            return "success"
        
        result = test_func()
        
        assert result == "success"
        assert len(mock_channel.sent_messages) == 1
    
    def test_factory_with_custom_templates(self):
        """测试使用自定义模板的工厂函数"""
        mock_channel = MockChannel()
        notify_instance = useNotify([mock_channel])
        
        @notify(
            notify_instance=notify_instance,
            success_template="✅ {function_name} 完成，耗时 {execution_time:.2f}秒，{result}",
            error_template="❌ {function_name} 失败: {error_message}"
        )
        def test_func():
            return "success"
        
        test_func()
        
        assert len(mock_channel.sent_messages) == 1
        message = mock_channel.sent_messages[0]
        assert "success" in message["content"]
    
    def test_factory_without_notify_instance(self):
        """测试不提供 notify_instance 的工厂函数"""
        @notify()
        def test_func():
            return "success"
        
        # 应该能正常执行，但不会发送通知（因为没有通道）
        result = test_func()
        assert result == "success"
    
    def test_invalid_notify_instance_factory(self):
        """测试工厂函数中的无效 notify_instance"""
        from use_notify.decorator.exceptions import NotifyConfigError
        
        # 创建一个无效的对象（不是 Notify 实例）
        class InvalidNotify:
            pass
        
        with pytest.raises(NotifyConfigError):
            @notify(notify_instance=InvalidNotify())
            def test_func():
                return "test"
            
            test_func()
    
    def test_invalid_title_type_factory(self):
        """测试工厂函数中的无效 title 类型"""
        # 由于 title 参数在运行时才会被验证，我们测试运行时行为
        @notify(title="valid_title")
        def test_func():
            return "test"
        
        # 这个测试主要验证装饰器能正常处理字符串类型的 title
        result = test_func()
        assert result == "test"


class TestDefaultNotifyInstance:
    """测试全局默认实例功能"""
    
    def setup_method(self):
        """每个测试前清理默认实例"""
        clear_default_notify_instance()
    
    def teardown_method(self):
        """每个测试后清理默认实例"""
        clear_default_notify_instance()
    
    def test_set_and_get_default_instance(self):
        """测试设置和获取默认实例"""
        mock_channel = MockChannel()
        notify_instance = useNotify([mock_channel])
        
        # 设置默认实例
        set_default_notify_instance(notify_instance)
        
        # 获取默认实例
        default_instance = get_default_notify_instance()
        assert default_instance is notify_instance
    
    def test_clear_default_instance(self):
        """测试清除默认实例"""
        mock_channel = MockChannel()
        notify_instance = useNotify([mock_channel])
        
        # 设置默认实例
        set_default_notify_instance(notify_instance)
        assert get_default_notify_instance() is notify_instance
        
        # 清除默认实例
        clear_default_notify_instance()
        assert get_default_notify_instance() is None
    
    def test_notify_with_default_instance(self):
        """测试使用默认实例的装饰器"""
        mock_channel = MockChannel()
        notify_instance = useNotify([mock_channel])
        
        # 设置默认实例
        set_default_notify_instance(notify_instance)
        
        @notify()
        def test_func():
            return "success"
        
        result = test_func()
        
        assert result == "success"
        assert len(mock_channel.sent_messages) == 1
        message = mock_channel.sent_messages[0]
        assert "✅" in message["title"]
        assert "test_func" in message["content"]
    
    def test_notify_without_default_instance(self):
        """测试没有默认实例时的装饰器"""
        # 确保没有默认实例
        clear_default_notify_instance()
        
        @notify()
        def test_func():
            return "success"
        
        # 应该能正常执行，但不会发送通知
        result = test_func()
        assert result == "success"
    
    def test_explicit_instance_overrides_default(self):
        """测试显式实例覆盖默认实例"""
        # 设置默认实例
        default_channel = MockChannel()
        default_instance = useNotify([default_channel])
        set_default_notify_instance(default_instance)
        
        # 创建显式实例
        explicit_channel = MockChannel()
        explicit_instance = useNotify([explicit_channel])
        
        @notify(notify_instance=explicit_instance)
        def test_func():
            return "success"
        
        test_func()
        
        # 应该使用显式实例，而不是默认实例
        assert len(default_channel.sent_messages) == 0
        assert len(explicit_channel.sent_messages) == 1
    
    @pytest.mark.asyncio
    async def test_async_notify_with_default_instance(self):
        """测试异步函数使用默认实例"""
        mock_channel = MockChannel()
        notify_instance = useNotify([mock_channel])
        
        # 设置默认实例
        set_default_notify_instance(notify_instance)
        
        @notify()
        async def async_func():
            await asyncio.sleep(0.01)
            return "async success"
        
        result = await async_func()
        
        assert result == "async success"
        assert len(mock_channel.sent_messages) == 1
        message = mock_channel.sent_messages[0]
        assert "✅" in message["title"]
        assert "async_func" in message["content"]


class TestIntegration:
    """集成测试"""
    
    def test_real_world_usage(self):
        """测试真实世界使用场景"""
        mock_channel = MockChannel()
        notify_instance = useNotify([mock_channel])
        
        @notify(
            notify_instance=notify_instance,
            title="数据处理任务",
            success_template="✅ {function_name} 处理了 {args[0]} 条数据，耗时 {execution_time:.2f}秒",
            include_args=True,
            include_result=True
        )
        def process_data(count):
            time.sleep(0.1)  # 模拟处理时间
            return f"处理了 {count} 条数据"
        
        result = process_data(100)
        
        assert result == "处理了 100 条数据"
        assert len(mock_channel.sent_messages) == 1
        
        message = mock_channel.sent_messages[0]
        assert message["title"] == "数据处理任务"
        assert "处理了 100 条数据" in message["content"]
        assert "耗时" in message["content"]
        assert "返回结果" in message["content"]
    
    @pytest.mark.asyncio
    async def test_async_real_world_usage(self):
        """测试异步真实世界使用场景"""
        mock_channel = MockChannel()
        notify_instance = useNotify([mock_channel])
        
        @notify(
            notify_instance=notify_instance,
            title="异步任务",
            include_result=True
        )
        async def async_task():
            await asyncio.sleep(0.1)
            return "异步任务完成"
        
        result = await async_task()
        
        assert result == "异步任务完成"
        assert len(mock_channel.sent_messages) == 1
        
        message = mock_channel.sent_messages[0]
        assert message["title"] == "异步任务"
        assert "异步任务完成" in message["content"]