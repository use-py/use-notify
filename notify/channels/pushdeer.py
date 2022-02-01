# -*- coding: utf-8 -*-
import requests
import logging

from notify.notification import Notification

logger = logging.getLogger(__name__)


class PushDeer(Notification):
    """pushdeer app 消息通知"""
    def __init__(self, settings):
        self.token = settings.PUSHDEER.TOKEN

    def send_message(self, content, title=None):
        text = f"{title}\n{content}"
        api_url = f'https://api2.pushdeer.com/message/push?pushkey={self.token}&text={text}'
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        requests.get(api_url, headers=headers)
        logger.debug("pushdeer消息推送成功")

    @classmethod
    def from_settings(cls, settings):
        return cls(settings)