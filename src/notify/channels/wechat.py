# -*- coding: utf-8 -*-
import json
import logging

import httpx

from .base import BaseChannel

logger = logging.getLogger(__name__)


class WeChat(BaseChannel):
    """企业微信消息通知"""

    def send(self, content, title=None):
        api_url = f'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={self.config.token}'
        api_body = {"markdown": {"content": content}, "msgtype": "markdown"}
        api_body = json.dumps(api_body).encode('utf-8')
        headers = {'Content-Type': 'application/json'}
        with httpx.Client() as client:
            client.post(api_url, json=api_body, headers=headers)
        logger.debug("WeChat消息推送成功")
