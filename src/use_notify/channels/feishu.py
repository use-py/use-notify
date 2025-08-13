# -*- coding: utf-8 -*-
import logging

import httpx

from .base import BaseChannel

logger = logging.getLogger(__name__)


class Feishu(BaseChannel):
    """飞书消息通知
    https://open.feishu.cn/document/client-docs/bot-v3/add-custom-bot?lang=zh-CN
    """

    @property
    def api_url(self):
        return f"https://open.feishu.cn/open-apis/bot/v2/hook/{self.config.token}"

    @property
    def headers(self):
        return {"Content-Type": "application/json"}

    def build_api_body(self, content, title=None):
        title = title or "消息提醒"
        api_body_content = [{
            "tag": "text",
            "text": content
        }]

        if self.config.at_all:
            api_body_content.append({"tag": "at", "user_id": "all"})
        if self.config.at_user_ids:
            api_body_content.extend([{"tag": "at", "user_id": user_id_} for user_id_ in self.config.at_user_ids])

        return {
            "msg_type": "post",
            "content": {
                "post": {
                    "zh_cn": {
                        "title": title,
                        "content": [
                            api_body_content
                        ]
                    }
                }
            }
        }

    def send(self, content, title=None):
        api_body = self.build_api_body(content, title)
        with httpx.Client() as client:
            response = client.post(self.api_url, json=api_body, headers=self.headers)
            response.raise_for_status()
        logger.debug("`飞书` send successfully")

    async def send_async(self, content, title=None):
        api_body = self.build_api_body(content, title)
        async with httpx.AsyncClient() as client:
            response = await client.post(self.api_url, json=api_body, headers=self.headers)
            response.raise_for_status()
        logger.debug("`飞书` send successfully")
