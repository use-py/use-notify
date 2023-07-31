# -*- coding: utf-8 -*-
import logging

import httpx

from .base import BaseChannel

logger = logging.getLogger(__name__)


class Ding(BaseChannel):
    """钉钉消息通知
    https://developers.dingtalk.com/document/app/custom-robot-access?spm=ding_open_doc.document.0.0.6d9d28e1QcCPII#topic-2026027
    """
    @property
    def api_url(self):
        return f'https://oapi.dingtalk.com/robot/send?access_token={self.config.token}'

    @property
    def headers(self):
        return {'Content-Type': 'application/json'}

    def build_api_body(self, content, title=None):
        title = title or '消息提醒'
        return {
            "msgtype": "markdown",
            "markdown": {"title": title, "text": content},
            "at": {"isAtAll": self.config.at_all}
        }

    def send(self, content, title=None):
        api_body = self.build_api_body(content, title)
        with httpx.Client() as client:
            client.post(self.api_url, json=api_body, headers=self.headers)
        logger.debug("`钉钉` send successfully")

    async def send_async(self, content, title=None):
        api_body = self.build_api_body(content, title)
        async with httpx.AsyncClient() as client:
            await client.post(self.api_url, json=api_body, headers=self.headers)
        logger.debug("`钉钉` send successfully")
