# -*- coding: utf-8 -*-
import logging

import httpx

from .base import BaseChannel

logger = logging.getLogger(__name__)


class Chanify(BaseChannel):
    """chanify 消息通知"""

    def send(self, content, title=None):
        text = f"{title}\n{content}"
        api_url = f'https://api.chanify.net/v1/sender/{self.config.token}'
        api_data = {'text': text}
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        with httpx.Client() as client:
            client.post(api_url, data=api_data, headers=headers)
        logger.debug("chanify消息推送成功")
