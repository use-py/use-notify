# -*- coding: utf-8 -*-
"""
通知发送器，处理通知发送逻辑
"""

import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
from typing import Optional

from ..notification import Notify


logger = logging.getLogger(__name__)


class NotificationSender:
    """通知发送器"""

    def __init__(
        self,
        notify_instance: Notify,
        timeout: Optional[float] = None
    ):
        self.notify_instance = notify_instance
        self.timeout = timeout

    def send_notification(self, title: str, content: str) -> None:
        """发送同步通知"""
        try:
            if self.timeout:
                # 使用线程池执行同步调用，实现超时控制
                # 无论是否在异步事件循环中，都能正确应用超时
                executor = ThreadPoolExecutor(max_workers=1)
                try:
                    future = executor.submit(
                        self.notify_instance.publish, title=title, content=content
                    )
                    future.result(timeout=self.timeout)
                finally:
                    # 使用 shutdown(wait=False) 立即关闭线程池，不等待线程完成
                    executor.shutdown(wait=False)
            else:
                self.notify_instance.publish(title=title, content=content)

            logger.info(f"通知发送成功: {title}")

        except FutureTimeoutError:
            error_msg = f"通知发送超时（{self.timeout}秒）"
            logger.warning(error_msg)
            self._handle_send_error(asyncio.TimeoutError(error_msg))
        except Exception as error:
            self._handle_send_error(error)

    async def send_notification_async(self, title: str, content: str) -> None:
        """发送异步通知"""
        try:
            if self.timeout:
                await asyncio.wait_for(
                    self._send_async_internal(title, content),
                    timeout=self.timeout
                )
            else:
                await self._send_async_internal(title, content)

            logger.info(f"异步通知发送成功: {title}")

        except Exception as error:
            self._handle_send_error(error)

    async def _send_async_internal(self, title: str, content: str) -> None:
        """内部异步发送方法"""
        await self.notify_instance.publish_async(title=title, content=content)

    def _handle_send_error(self, error: Exception) -> None:
        """处理发送错误"""
        error_msg = f"通知发送失败: {str(error)}"
        logger.warning(error_msg)

        # 记录详细错误信息但不抛出异常，避免影响原函数执行
        logger.debug(f"通知发送错误详情: {error}", exc_info=True)

        # 可以选择是否抛出异常，根据需求决定
        # 默认情况下不抛出，只记录日志
        # raise NotifySendError(error_msg) from error
