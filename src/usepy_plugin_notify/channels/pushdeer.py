# -*- coding: utf-8 -*-
import logging

import httpx

from .base import BaseChannel

logger = logging.getLogger(__name__)


class PushDeer(BaseChannel):
    """pushdeer app 消息通知"""

    @property
    def api_url(self):
        return f'https://api2.pushdeer.com/message/push?pushkey={self.config.token}&text={{text}}'

    @property
    def headers(self):
        return {'Content-Type': 'application/x-www-form-urlencoded'}

    def build_api_body(self, content, title=None):
        return self.api_url.format_map({"text": f"{title}\n{content}"})

    def send(self, content, title=None):
        api_url = self.build_api_body(content, title)
        with httpx.Client() as client:
            client.get(api_url, headers=self.headers)
        logger.debug("`pushdeer` send successfully")

    async def send_async(self, content, title=None):
        api_url = self.build_api_body(content, title)
        async with httpx.AsyncClient() as client:
            await client.get(api_url, headers=self.headers)
        logger.debug("`pushdeer` send successfully")