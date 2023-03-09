# -*- coding: utf-8 -*-
import httpx
import logging

from .base import BaseChannel

logger = logging.getLogger(__name__)


class PushDeer(BaseChannel):
    """pushdeer app 消息通知"""

    def send(self, content, title=None):
        text = f"{title}\n{content}"
        api_url = f'https://api2.pushdeer.com/message/push?pushkey={self.config.token}&text={text}'
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        with httpx.Client() as client:
            client.get(api_url, headers=headers)
        logger.debug("pushdeer消息推送成功")
