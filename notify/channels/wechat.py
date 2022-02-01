# -*- coding: utf-8 -*-
import json
import logging

import requests

from notify.notification import Notification

logger = logging.getLogger(__name__)


class WeChat(Notification):
    """企业微信消息通知"""
    def __init__(self, settings):
        self.token = settings.WECHAT.ACCESS_TOKEN

    def send_message(self, content, title=None):
        api_url = f'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={self.token}'
        api_body = {"markdown": {"content": content}, "msgtype": "markdown"}
        api_body = json.dumps(api_body).encode('utf-8')
        headers = {'Content-Type': 'application/json'}
        requests.post(api_url, data=api_body, headers=headers)
        logger.debug("WeChat消息推送成功")

    @classmethod
    def from_settings(cls, settings):
        return cls(settings)
