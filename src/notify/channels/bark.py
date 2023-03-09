# -*- coding: utf-8 -*-
import logging
import httpx

from .base import BaseChannel

logger = logging.getLogger(__name__)


class Bark(BaseChannel):
    """Bark app 消息通知"""

    def send(self, content, title=None):
        api_url = f'https://api.day.app/{self.config.token}/{title}/{content}'
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        with httpx.Client() as client:
            client.get(api_url, headers=headers)
        logger.debug("bark消息推送成功")
