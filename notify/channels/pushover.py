# -*- coding: utf-8 -*-
import logging

import requests

from notify.notification import Notification

logger = logging.getLogger(__name__)


class PushOver(Notification):
    """pushover app 消息通知"""
    def __init__(self, settings):
        self.token = settings.PUSHOVER.TOKEN
        self.user = settings.PUSHOVER.USER

    def send_message(self, content, title=None):
        api_url = 'https://api.pushover.net/1/messages.json'
        api_body = {
            'token': self.token,
            'user': self.user,
            'title': title,
            'message': content,
        }
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        requests.post(api_url, data=api_body, headers=headers)
        logger.debug("pushover消息推送成功")

    @classmethod
    def from_settings(cls, settings):
        return cls(settings)
