# -*- coding: utf-8 -*-
import logging

import requests

from notify.notification import Notification

logger = logging.getLogger(__name__)


class Chanify(Notification):
    """chanify 消息通知"""

    def __init__(self, settings):
        self.token = settings.CHANIFY.TOKEN

    def send_message(self, content, title=None):
        text = f"{title}\n{content}"
        api_url = f'https://api.chanify.net/v1/sender/{self.token}'
        api_data = {'text': text}
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        requests.post(api_url, data=api_data, headers=headers)
        logger.debug("chanify消息推送成功")

    @classmethod
    def from_settings(cls, settings):
        return cls(settings)
