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

    def build_api_body(self, title, content):
        content = f"## {title}\n\n{content}"
        api_body = {"markdown": {"content": content}, "msgtype": "markdown"}

        if self.config.mentioned_list:
            api_body["markdown"]["mentioned_list"] = self.config.mentioned_list
        if self.config.mentioned_mobile_list:
            api_body["markdown"]["mentioned_mobile_list"] = self.config.mentioned_mobile_list
        
        return api_body

    def send(self, content, title=None):
        api_body = self.build_api_body(title, content)
        with httpx.Client() as client:
            response = client.post(self.api_url, json=api_body, headers=self.headers)
            response.raise_for_status()
        logger.debug("`WeChat` send successfully")

    async def send_async(self, content, title=None):
        api_body = self.build_api_body(title, content)
        async with httpx.AsyncClient() as client:
            response = await client.post(self.api_url, json=api_body, headers=self.headers)
            response.raise_for_status()
        logger.debug("`WeChat` send successfully")
