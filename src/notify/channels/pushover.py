# -*- coding: utf-8 -*-
import logging

import httpx

from .base import BaseChannel

logger = logging.getLogger(__name__)


class PushOver(BaseChannel):
    """pushover app 消息通知"""

    def send(self, content, title=None):
        api_url = 'https://api.pushover.net/1/messages.json'
        api_body = {
            'token': self.config.token,
            'user': self.config.user,
            'title': title,
            'message': content,
        }
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        with httpx.Client() as client:
            client.post(api_url, data=api_body, headers=headers)
        logger.debug("pushover消息推送成功")
