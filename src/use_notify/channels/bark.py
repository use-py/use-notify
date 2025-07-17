# -*- coding: utf-8 -*-
import logging

import httpx

from .base import BaseChannel

logger = logging.getLogger(__name__)


class Bark(BaseChannel):
    """Bark app 消息通知"""

    @property
    def api_url(self):
        # Check if base_url exists in config, otherwise use default
        if self.config.base_url:
            base_url = self.config.base_url.rstrip("/")
        else:
            base_url = "https://api.day.app"
        
        return f"{base_url}/{self.config.token}"

    @property
    def headers(self):
        return {"Content-Type": "application/json; charset=utf-8"}

    def _prepare_payload(self, content, title=None):
        payload = {
            "body": content,
        }
        
        if title:
            payload["title"] = title
            
        # Optional parameters from config
        for param in ["badge", "sound", "icon", "group", "url"]:
            if hasattr(self.config, param) and getattr(self.config, param) is not None:
                payload[param] = getattr(self.config, param)
                
        return payload

    def send(self, content, title=None):
        payload = self._prepare_payload(content, title)
        with httpx.Client() as client:
            response = client.post(self.api_url, headers=self.headers, json=payload)
            response.raise_for_status()
        logger.debug("`bark` send successfully")

    async def send_async(self, content, title=None):
        payload = self._prepare_payload(content, title)
        async with httpx.AsyncClient() as client:
            response = await client.post(self.api_url, headers=self.headers, json=payload)
            response.raise_for_status()
        logger.debug("`bark` send successfully")
