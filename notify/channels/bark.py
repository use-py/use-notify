# -*- coding: utf-8 -*-
import logging

import requests

from notify.notification import Notification

logger = logging.getLogger(__name__)


class Bark(Notification):
    """Bark app 消息通知"""
    def __init__(self, settings):
        self.token = settings.BARK.TOKEN

    def send_message(self, content, title=None):
        api_url = f'https://api.day.app/{self.token}/{title}/{content}'
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        requests.get(api_url, headers=headers)
        logger.debug("bark消息推送成功")

    @classmethod
    def from_settings(cls, settings):
        return cls(settings)
