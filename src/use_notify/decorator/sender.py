# -*- coding: utf-8 -*-
"""
通知发送器，处理通知发送逻辑
"""

import asyncio
import logging
from typing import Optional

from ..notification import Notify
from .exceptions import NotifySendError


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
                # 对于同步调用，我们使用 asyncio.wait_for 来实现超时
                # 但这需要在异步上下文中运行，所以我们创建一个新的事件循环
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        # 如果已经在事件循环中，直接调用
                        self.notify_instance.publish(title=title, content=content)
                    else:
                        # 如果不在事件循环中，使用 run_until_complete
                        loop.run_until_complete(
                            asyncio.wait_for(
                                self._send_async_internal(title, content),
                                timeout=self.timeout
                            )
                        )
                except RuntimeError:
                    # 如果没有事件循环，创建一个新的
                    asyncio.run(
                        asyncio.wait_for(
                            self._send_async_internal(title, content),
                            timeout=self.timeout
                        )
                    )
            else:
                self.notify_instance.publish(title=title, content=content)
            
            logger.info(f"通知发送成功: {title}")
            
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