# -*- coding: utf-8 -*-
import json
import logging

import httpx

from .base import BaseChannel

logger = logging.getLogger(__name__)


class Ding(BaseChannel):
    """钉钉消息通知"""

    def send(self, content, title=None):
        """
        https://developers.dingtalk.com/document/app/custom-robot-access?spm=ding_open_doc.document.0.0.6d9d28e1QcCPII#topic-2026027
        """
        title = title or '消息提醒'
        api_url = f'https://oapi.dingtalk.com/robot/send?access_token={self.config.token}'
        api_body = {"msgtype": "markdown",
                    "markdown": {"title": title, "text": content},
                    "at": {"isAtAll": self.config.at_all}}
        headers = {'Content-Type': 'application/json'}
        with httpx.Client() as client:
            client.post(api_url, json=api_body, headers=headers)
        logger.debug("钉钉消息推送成功")
