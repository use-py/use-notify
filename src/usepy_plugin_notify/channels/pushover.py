# -*- coding: utf-8 -*-
import logging

import httpx

from .base import BaseChannel

logger = logging.getLogger(__name__)


class PushOver(BaseChannel):
    """pushover app 消息通知"""

    @property
    def api_url(self):
        return 'https://api.pushover.net/1/messages.json'

    @property
    def headers(self):
        return {'Content-Type': 'application/x-www-form-urlencoded'}

    def build_api_body(self, content, title=None):
        return {
            'token': self.config.token,
            'user': self.config.user,
            'title': title,
            'message': content,
        }

    def send(self, content, title=None):
        api_body = self.build_api_body(content, title)
        with httpx.Client() as client:
            client.post(self.api_url, data=api_body, headers=self.headers)
        logger.debug("`pushover` send successfully")

    async def send_async(self, content, title=None):
        api_body = self.build_api_body(content, title)
        async with httpx.AsyncClient() as client:
            await client.post(self.api_url, data=api_body, headers=self.headers)
        logger.debug("`pushover` send successfully")
