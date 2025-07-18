# -*- coding: utf-8 -*-
import logging
from urllib.parse import quote

import httpx

from .base import BaseChannel

logger = logging.getLogger(__name__)


class PushDeer(BaseChannel):
    """pushdeer app 消息通知

    支持三种消息类型:
    - text: 纯文本消息 (默认)
    - image: 图片消息
    - markdown: Markdown格式消息

    配置参数:
    - token: PushDeer的pushkey
    - base_url: 可选，自建PushDeer服务的URL，默认为"https://api2.pushdeer.com"
    - type: 可选，消息类型，可选值为text、markdown、image，默认为text
    """

    @property
    def api_url(self):
        """获取PushDeer API基础URL"""
        # 确保token存在
        if not self.config.token:
            raise ValueError("PushDeer token (pushkey) is required")

        # Check if base_url exists in config, otherwise use default
        if self.config.base_url:
            base_url = self.config.base_url.rstrip("/")
        else:
            base_url = "https://api2.pushdeer.com"

        return f"{base_url}/message/push"

    def _prepare_params(self, content, title=None):
        """准备请求参数

        Args:
            content: 消息内容
            title: 消息标题

        Returns:
            dict: 请求参数
        """
        # 默认标题
        if not title:
            title = "消息提醒"

        # 确定消息类型
        msg_type = getattr(self.config, "type", "markdown")
        if msg_type not in ["text", "markdown", "image"]:
            if msg_type:  # 只有当type不为空且无效时才记录警告
                logger.warning(f"Invalid message type: {msg_type}, fallback to text")
            msg_type = "markdown"

        params = {"pushkey": self.config.token, "text": title, "type": msg_type}

        # 根据消息类型处理内容
        if msg_type == "text":
            # 对于text类型，content直接作为text参数
            params["text"] = content
        elif msg_type == "markdown":
            # 对于markdown类型，content作为desp参数
            params["desp"] = content
        elif msg_type == "image":
            # 对于image类型，content应该是图片URL
            params["desp"] = content

        return params

    @property
    def headers(self):
        """请求头"""
        return {"Content-Type": "application/x-www-form-urlencoded"}

    def send(self, content, title=None):
        """发送PushDeer消息

        Args:
            content: 消息内容
            title: 消息标题
        """
        params = self._prepare_params(content, title)

        with httpx.Client() as client:
            response = client.get(self.api_url, params=params, headers=self.headers)
            response.raise_for_status()
        logger.debug("`pushdeer` send message successfully")

    async def send_async(self, content, title=None):
        """异步发送PushDeer消息

        Args:
            content: 消息内容
            title: 消息标题
        """
        params = self._prepare_params(content, title)

        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.api_url, params=params, headers=self.headers
            )
            response.raise_for_status()
        logger.debug("`pushdeer` send message successfully")
