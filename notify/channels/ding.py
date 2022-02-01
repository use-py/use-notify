# -*- coding: utf-8 -*-
import json
import logging

import requests

from notify.notification import Notification

logger = logging.getLogger(__name__)


class Ding(Notification):
    """钉钉消息通知"""
    def __init__(self, settings):
        self.access_token = settings.DING.ACCESS_TOKEN
        self.at_all = settings.DING.AT_ALL

    def send_message(self, content, title=None):
        """
        https://developers.dingtalk.com/document/app/custom-robot-access?spm=ding_open_doc.document.0.0.6d9d28e1QcCPII#topic-2026027
        """
        title = title or '消息提醒'
        api_url = f'https://oapi.dingtalk.com/robot/send?access_token={self.access_token}'
        api_body = {"msgtype": "markdown",
                    "markdown": {"title": title, "text": content},
                    "at": {"isAtAll": self.at_all}}
        api_body = json.dumps(api_body).encode('utf-8')
        headers = {'Content-Type': 'application/json'}
        requests.post(api_url, data=api_body, headers=headers)
        logger.debug("钉钉消息推送成功")

    @classmethod
    def from_settings(cls, settings):
        return cls(settings)
