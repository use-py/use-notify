# -*- coding: utf-8 -*-
import logging
import httpx

from .base import BaseChannel

logger = logging.getLogger(__name__)


class Bark(BaseChannel):
    """Bark app 消息通知"""

    @property
    def api_url(self):
        return f'https://api.day.app/{self.config.token}/{{title}}/{{content}}'

    @property
    def headers(self):
        return {'Content-Type': 'application/x-www-form-urlencoded'}

    def send(self, content, title=None):
        api_url = self.api_url.format_map({"content": content, "title": title})
        with httpx.Client() as client:
            client.get(api_url, headers=self.headers)
        logger.debug("`bark` send successfully")

    async def send_async(self, content, title=None):
        api_url = self.api_url.format_map({"content": content, "title": title})
        async with httpx.AsyncClient() as client:
            await client.get(api_url, headers=self.headers)
        logger.debug("`bark` send successfully")
