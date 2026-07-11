# -*- coding: utf-8 -*-
from .http import HttpChannel


class Feishu(HttpChannel):
    """飞书消息通知
    https://open.feishu.cn/document/client-docs/bot-v3/add-custom-bot?lang=zh-CN
    """

    payload_kind = "json"
    provider_name = "feishu"
    success_fields = {"code": {0}}
    success_log_message = "`飞书` send successfully"

    @property
    def api_url(self):
        return f"https://open.feishu.cn/open-apis/bot/v2/hook/{self.resolve_config_value('token')}"

    @property
    def headers(self):
        return {"Content-Type": "application/json"}

    def build_api_body(self, content, title=None):
        title = title or "消息提醒"
        api_body_content = [{"tag": "text", "text": content}]

        if self.config.at_all:
            api_body_content.append({"tag": "at", "user_id": "all"})
        if self.config.at_user_ids:
            api_body_content.extend(
                [{"tag": "at", "user_id": user_id_} for user_id_ in self.config.at_user_ids]
            )

        return {
            "msg_type": "post",
            "content": {"post": {"zh_cn": {"title": title, "content": [api_body_content]}}},
        }

    def build_request_payload(self, content, title=None):
        return self.build_api_body(content, title)
