# -*- coding: utf-8 -*-
import logging

import httpx

from .base import BaseChannel

logger = logging.getLogger(__name__)


class Chanify(BaseChannel):
    """chanify 消息通知"""

    @property
    def api_url(self):
        return f'https://api.chanify.net/v1/sender/{self.config.token}'

    @property
    def headers(self):
        return {'Content-Type': 'application/x-www-form-urlencoded'}

    @staticmethod
    def build_api_body(content, title=None):
        return {'text': f"{title}\n{content}"}

    def send(self, content, title=None):
        api_body = self.build_api_body(content, title)
        with httpx.Client() as client:
            client.post(self.api_url, data=api_body, headers=self.headers)
        logger.debug("`chanify` send successfully")

    async def send_async(self, content, title=None):
        api_body = self.build_api_body(content, title)
        async with httpx.AsyncClient() as client:
            await client.post(self.api_url, data=api_body, headers=self.headers)
        logger.debug("`chanify` send successfully")
