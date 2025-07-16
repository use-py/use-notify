# -*- coding: utf-8 -*-
import logging

import httpx

from .base import BaseChannel

logger = logging.getLogger(__name__)


class WeChat(BaseChannel):
    """企业微信消息通知"""

    @property
    def api_url(self):
        return (
            f"https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={self.config.token}"
        )

    @property
    def headers(self):
        return {"Content-Type": "application/json"}

    @staticmethod
    def build_api_body(title, content):
        content = f"## {title}\n\n{content}"
        api_body = {"markdown": {"content": content}, "msgtype": "markdown"}
        return api_body

    def send(self, content, title=None):
        api_body = self.build_api_body(title, content)
        with httpx.Client() as client:
            client.post(self.api_url, json=api_body, headers=self.headers)
        logger.debug("`WeChat` send successfully")

    async def send_async(self, content, title=None):
        api_body = self.build_api_body(title, content)
        async with httpx.AsyncClient() as client:
            await client.post(self.api_url, json=api_body, headers=self.headers)
        logger.debug("`WeChat` send successfully")
