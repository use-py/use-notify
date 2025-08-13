# -*- coding: utf-8 -*-
import logging

import httpx

from .base import BaseChannel

logger = logging.getLogger(__name__)


class Chanify(BaseChannel):
    """chanify 消息通知"""

    @property
    def api_url(self):
        # Check if base_url exists in config, otherwise use default
        if self.config.base_url:
            base_url = self.config.base_url.rstrip("/")
        else:
            base_url = "https://api.chanify.net"
        
        return f"{base_url}/v1/sender/{self.config.token}"

    @property
    def headers(self):
        return {"Content-Type": "application/x-www-form-urlencoded"}

    @staticmethod
    def build_api_body(content, title=None):
        return {"text": f"{title}\n{content}"}

    def send(self, content, title=None):
        api_body = self.build_api_body(content, title)
        with httpx.Client() as client:
            response = client.post(self.api_url, data=api_body, headers=self.headers)
            response.raise_for_status()
        logger.debug("`chanify` send successfully")

    async def send_async(self, content, title=None):
        api_body = self.build_api_body(content, title)
        async with httpx.AsyncClient() as client:
            response = await client.post(self.api_url, data=api_body, headers=self.headers)
            response.raise_for_status()
        logger.debug("`chanify` send successfully")
