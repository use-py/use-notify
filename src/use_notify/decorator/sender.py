# -*- coding: utf-8 -*-
"""
通知发送器，处理通知发送逻辑
"""

import asyncio
import logging
import threading
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FutureTimeoutError
from typing import Optional

from ..notification import Notify

logger = logging.getLogger(__name__)


class NotificationSender:
    """通知发送器"""

    SYNC_TIMEOUT_WORKERS = 4
    _sync_timeout_executor = ThreadPoolExecutor(
        max_workers=SYNC_TIMEOUT_WORKERS,
        thread_name_prefix="use-notify-sync-timeout",
    )
    _sync_timeout_slots = threading.BoundedSemaphore(SYNC_TIMEOUT_WORKERS)

    def __init__(self, notify_instance: Notify, timeout: Optional[float] = None):
        self.notify_instance = notify_instance
        self.timeout = timeout

    def send_notification(self, title: str, content: str) -> None:
        """发送同步通知"""
        try:
            if self.timeout:
                # Python cannot stop a running sync send safely. Keep timed-out
                # work bounded so callers return quickly without unbounded threads.
                self._send_sync_with_timeout(title, content)
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
                    self._send_async_internal(title, content), timeout=self.timeout
                )
            else:
                await self._send_async_internal(title, content)

            logger.info(f"异步通知发送成功: {title}")

        except Exception as error:
            self._handle_send_error(error)

    async def _send_async_internal(self, title: str, content: str) -> None:
        """内部异步发送方法"""
        await self.notify_instance.publish_async(title=title, content=content)

    def _send_sync_with_timeout(self, title: str, content: str) -> None:
        if not self._sync_timeout_slots.acquire(blocking=False):
            raise asyncio.TimeoutError(
                f"同步通知后台 worker 已满（最多 {self.SYNC_TIMEOUT_WORKERS} 个）"
            )

        try:
            future = self._sync_timeout_executor.submit(
                self.notify_instance.publish, title=title, content=content
            )
        except Exception:
            self._sync_timeout_slots.release()
            raise

        future.add_done_callback(self._release_sync_timeout_slot)
        try:
            future.result(timeout=self.timeout)
        except FutureTimeoutError:
            future.cancel()
            raise

    @classmethod
    def _release_sync_timeout_slot(cls, _future) -> None:
        cls._sync_timeout_slots.release()

    def _handle_send_error(self, error: Exception) -> None:
        """处理发送错误"""
        error_msg = f"通知发送失败: {str(error)}"
        logger.warning(error_msg)

        # 记录详细错误信息但不抛出异常，避免影响原函数执行
        logger.debug(f"通知发送错误详情: {error}", exc_info=True)

        # 可以选择是否抛出异常，根据需求决定
        # 默认情况下不抛出，只记录日志
        # raise NotifySendError(error_msg) from error
