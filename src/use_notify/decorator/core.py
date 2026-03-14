# -*- coding: utf-8 -*-
"""
核心装饰器实现
"""

import asyncio
from contextvars import ContextVar
import functools
import inspect
import logging
import threading
from datetime import datetime
from typing import Callable, Optional, Sequence, Type

from ..notification import Notify
from .context import ExecutionContext
from .exceptions import NotifyConfigError
from .formatter import MessageFormatter
from .sender import NotificationSender


logger = logging.getLogger(__name__)

# 默认通知实例，按当前执行上下文隔离，避免线程/任务间相互污染
_default_notify_instance_var: ContextVar[Optional[Notify]] = ContextVar(
    "use_notify_default_instance",
    default=None,
)
RetriableExceptionsInput = Optional[Sequence[Type[BaseException]]]

# 线程锁，用于保护类级别共享状态
_decorators_lock = threading.Lock()


def set_default_notify_instance(notify_instance: Notify) -> None:
    """设置当前执行上下文的默认通知实例
    
    Args:
        notify_instance: 要设置为默认的 Notify 实例
    
    Example:
        # 设置默认通知实例
        default_notify = useNotify()
        default_notify.add(useNotifyChannel.Bark({"token": "your_token"}))
        set_default_notify_instance(default_notify)
        
        # 现在可以直接使用装饰器，无需传递 notify_instance
        @notify()
        def my_task():
            return "任务完成"
    """
    if not isinstance(notify_instance, Notify):
        raise NotifyConfigError("notify_instance 必须是 Notify 类的实例")
    _default_notify_instance_var.set(notify_instance)
    logger.info("已设置默认通知实例")


def get_default_notify_instance() -> Optional[Notify]:
    """获取当前执行上下文的默认通知实例
    
    Returns:
        当前的默认通知实例，如果未设置则返回 None
    """
    return _default_notify_instance_var.get()


def clear_default_notify_instance() -> None:
    """清除当前执行上下文的默认通知实例"""
    _default_notify_instance_var.set(None)
    logger.info("已清除默认通知实例")


class NotifyDecorator:
    """通知装饰器类"""

    # 类级别缓存，记录已发出警告的装饰器实例
    _warned_missing_default: set = set()

    def __init__(
        self,
        notify_instance: Optional[Notify] = None,
        title: Optional[str] = None,
        success_template: Optional[str] = None,
        error_template: Optional[str] = None,
        notify_on_success: bool = True,
        notify_on_error: bool = True,
        include_args: bool = False,
        include_result: bool = False,
        timeout: Optional[float] = None,
        max_retries: Optional[int] = None,
        retry_delay: Optional[float] = None,
        retry_backoff: Optional[float] = None,
        retriable_exceptions: RetriableExceptionsInput = None,
    ):
        # 验证配置
        self._validate_config(
            notify_instance, title, success_template, error_template,
            notify_on_success, notify_on_error, include_args, include_result, timeout,
            max_retries, retry_delay, retry_backoff, retriable_exceptions,
        )

        self.notify_instance = notify_instance
        self.title = title
        self.notify_on_success = notify_on_success
        self.notify_on_error = notify_on_error
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.retry_backoff = retry_backoff
        self.retriable_exceptions = retriable_exceptions
        # 使用装饰器实例的唯一ID作为标识
        self._instance_id = id(self)
        
        # 创建消息格式化器
        self.formatter = MessageFormatter(
            success_template=success_template,
            error_template=error_template,
            include_args=include_args,
            include_result=include_result
        )
        
    def __call__(self, func: Callable) -> Callable:
        """装饰器调用"""
        if inspect.iscoroutinefunction(func):
            return self._wrap_async_function(func)
        else:
            return self._wrap_sync_function(func)
    
    def _wrap_sync_function(self, func: Callable) -> Callable:
        """包装同步函数"""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 创建执行上下文
            context = ExecutionContext(
                function_name=func.__name__,
                start_time=datetime.now(),
                args=args,
                kwargs=kwargs
            )
            
            logger.debug(f"开始执行函数: {func.__name__}")
            
            try:
                # 执行原函数
                result = func(*args, **kwargs)
                
                # 标记成功
                context.mark_success(result)
                logger.debug(f"函数 {func.__name__} 执行成功，耗时 {context.execution_time:.2f}秒")
                
                # 发送成功通知
                if self.notify_on_success:
                    self._send_success_notification(context)
                
                return result
                
            except Exception as e:
                # 标记失败
                context.mark_error(e)
                logger.debug(f"函数 {func.__name__} 执行失败，耗时 {context.execution_time:.2f}秒")
                
                # 发送失败通知
                if self.notify_on_error:
                    self._send_error_notification(context)
                
                # 重新抛出异常
                raise
        
        return wrapper
    
    def _wrap_async_function(self, func: Callable) -> Callable:
        """包装异步函数"""
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            # 创建执行上下文
            context = ExecutionContext(
                function_name=func.__name__,
                start_time=datetime.now(),
                args=args,
                kwargs=kwargs
            )
            
            logger.debug(f"开始执行异步函数: {func.__name__}")
            
            try:
                # 执行原函数
                result = await func(*args, **kwargs)
                
                # 标记成功
                context.mark_success(result)
                logger.debug(f"异步函数 {func.__name__} 执行成功，耗时 {context.execution_time:.2f}秒")
                
                # 发送成功通知
                if self.notify_on_success:
                    await self._send_success_notification_async(context)
                
                return result
                
            except Exception as e:
                # 标记失败
                context.mark_error(e)
                logger.debug(f"异步函数 {func.__name__} 执行失败，耗时 {context.execution_time:.2f}秒")
                
                # 发送失败通知
                if self.notify_on_error:
                    await self._send_error_notification_async(context)
                
                # 重新抛出异常
                raise
        
        return async_wrapper
    
    def _send_success_notification(self, context: ExecutionContext) -> None:
        """发送成功通知（同步）"""
        try:
            message = self.formatter.format_success_message(context)
            title = self.title or message["title"]
            sender = self._build_sender()
            sender.send_notification(title, message["content"])
        except Exception as e:
            logger.warning(f"发送成功通知失败: {e}")
    
    async def _send_success_notification_async(self, context: ExecutionContext) -> None:
        """发送成功通知（异步）"""
        try:
            message = self.formatter.format_success_message(context)
            title = self.title or message["title"]
            sender = self._build_sender()
            await sender.send_notification_async(title, message["content"])
        except Exception as e:
            logger.warning(f"发送成功通知失败: {e}")
    
    def _send_error_notification(self, context: ExecutionContext) -> None:
        """发送错误通知（同步）"""
        try:
            message = self.formatter.format_error_message(context)
            title = self.title or message["title"]
            sender = self._build_sender()
            sender.send_notification(title, message["content"])
        except Exception as e:
            logger.warning(f"发送错误通知失败: {e}")
    
    async def _send_error_notification_async(self, context: ExecutionContext) -> None:
        """发送错误通知（异步）"""
        try:
            message = self.formatter.format_error_message(context)
            title = self.title or message["title"]
            sender = self._build_sender()
            await sender.send_notification_async(title, message["content"])
        except Exception as e:
            logger.warning(f"发送错误通知失败: {e}")

    def _build_sender(self) -> NotificationSender:
        notify_instance = self._resolve_notify_instance()
        return NotificationSender(notify_instance=notify_instance, timeout=self.timeout)

    def _resolve_notify_instance(self) -> Notify:
        notify_instance = self.notify_instance

        if notify_instance is None:
            notify_instance = get_default_notify_instance()
            if notify_instance is None:
                notify_instance = Notify()
                # 使用类级别缓存和锁避免多线程/多任务场景下的重复警告
                with _decorators_lock:
                    if self._instance_id not in self._warned_missing_default:
                        logger.warning(
                            "未提供 notify_instance 且当前执行上下文未设置默认实例，创建了一个空的 Notify 实例。请确保添加通知渠道或设置默认实例。"
                        )
                        self._warned_missing_default.add(self._instance_id)
            else:
                logger.debug("使用全局默认通知实例")

        return self._apply_retry_overrides(
            notify_instance=notify_instance,
            max_retries=self.max_retries,
            retry_delay=self.retry_delay,
            retry_backoff=self.retry_backoff,
            retriable_exceptions=self.retriable_exceptions,
        )
    
    def _validate_config(self, *args) -> None:
        """验证配置参数"""
        notify_instance, title, success_template, error_template, \
        notify_on_success, notify_on_error, include_args, include_result, timeout, \
        max_retries, retry_delay, retry_backoff, retriable_exceptions = args
        
        if notify_instance is not None and not isinstance(notify_instance, Notify):
            raise NotifyConfigError("notify_instance 必须是 Notify 类的实例")
        
        if title is not None and not isinstance(title, str):
            raise NotifyConfigError("title 必须是字符串")
        
        if success_template is not None and not isinstance(success_template, str):
            raise NotifyConfigError("success_template 必须是字符串")
        
        if error_template is not None and not isinstance(error_template, str):
            raise NotifyConfigError("error_template 必须是字符串")
        
        if not isinstance(notify_on_success, bool):
            raise NotifyConfigError("notify_on_success 必须是布尔值")
        
        if not isinstance(notify_on_error, bool):
            raise NotifyConfigError("notify_on_error 必须是布尔值")
        
        if not isinstance(include_args, bool):
            raise NotifyConfigError("include_args 必须是布尔值")
        
        if not isinstance(include_result, bool):
            raise NotifyConfigError("include_result 必须是布尔值")
        
        if timeout is not None and (not isinstance(timeout, (int, float)) or timeout <= 0):
            raise NotifyConfigError("timeout 必须是正数")

        if max_retries is not None and (not isinstance(max_retries, int) or max_retries < 0):
            raise NotifyConfigError("max_retries 必须是大于等于 0 的整数")

        if retry_delay is not None and (
            not isinstance(retry_delay, (int, float)) or retry_delay < 0
        ):
            raise NotifyConfigError("retry_delay 必须是大于等于 0 的数字")

        if retry_backoff is not None and (
            not isinstance(retry_backoff, (int, float)) or retry_backoff <= 0
        ):
            raise NotifyConfigError("retry_backoff 必须是正数")

        if retriable_exceptions is not None:
            if not isinstance(retriable_exceptions, (list, tuple)):
                raise NotifyConfigError("retriable_exceptions 必须是异常类型序列")
            invalid_types = [
                exception_type
                for exception_type in retriable_exceptions
                if not isinstance(exception_type, type)
                or not issubclass(exception_type, BaseException)
            ]
            if invalid_types:
                raise NotifyConfigError("retriable_exceptions 必须只包含异常类型")

        if not notify_on_success and not notify_on_error:
            raise NotifyConfigError("notify_on_success 和 notify_on_error 不能同时为 False")

    @staticmethod
    def _apply_retry_overrides(
        notify_instance: Notify,
        max_retries: Optional[int],
        retry_delay: Optional[float],
        retry_backoff: Optional[float],
        retriable_exceptions: RetriableExceptionsInput,
    ) -> Notify:
        if (
            max_retries is None
            and retry_delay is None
            and retry_backoff is None
            and retriable_exceptions is None
        ):
            return notify_instance

        retry_config = notify_instance.retry_config
        return Notify(
            channels=list(notify_instance.channels),
            max_retries=retry_config.max_retries if max_retries is None else max_retries,
            retry_delay=retry_config.retry_delay if retry_delay is None else retry_delay,
            retry_backoff=(
                retry_config.retry_backoff
                if retry_backoff is None
                else retry_backoff
            ),
            retriable_exceptions=(
                retry_config.retriable_exceptions
                if retriable_exceptions is None
                else tuple(retriable_exceptions)
            ),
        )


def notify(
    notify_instance: Optional[Notify] = None,
    title: Optional[str] = None,
    success_template: Optional[str] = None,
    error_template: Optional[str] = None,
    notify_on_success: bool = True,
    notify_on_error: bool = True,
    include_args: bool = False,
    include_result: bool = False,
    timeout: Optional[float] = None,
    max_retries: Optional[int] = None,
    retry_delay: Optional[float] = None,
    retry_backoff: Optional[float] = None,
    retriable_exceptions: RetriableExceptionsInput = None,
) -> Callable:
    """
    创建通知装饰器的工厂函数
    
    Args:
        notify_instance: Notify 实例，如果为 None 则创建空实例
        title: 自定义通知标题
        success_template: 成功消息模板
        error_template: 错误消息模板
        notify_on_success: 是否在成功时发送通知
        notify_on_error: 是否在失败时发送通知
        include_args: 是否在消息中包含函数参数
        include_result: 是否在消息中包含函数返回值
        timeout: 通知发送超时时间（秒）
        max_retries: 通知发送失败后的最大重试次数
        retry_delay: 每次重试前的延迟（秒）
        retry_backoff: 重试延迟的退避倍数
        retriable_exceptions: 额外视为可重试的异常类型序列
    
    Returns:
        装饰器函数
    
    Example:
        @notify()
        def my_function():
            return "Hello World"
        
        @notify(
            title="重要任务",
            success_template="✅ {function_name} 完成，耗时 {execution_time:.2f}秒",
            include_result=True
        )
        def important_task():
            return "任务完成"
    """
    return NotifyDecorator(
        notify_instance=notify_instance,
        title=title,
        success_template=success_template,
        error_template=error_template,
        notify_on_success=notify_on_success,
        notify_on_error=notify_on_error,
        include_args=include_args,
        include_result=include_result,
        timeout=timeout,
        max_retries=max_retries,
        retry_delay=retry_delay,
        retry_backoff=retry_backoff,
        retriable_exceptions=retriable_exceptions,
    )
