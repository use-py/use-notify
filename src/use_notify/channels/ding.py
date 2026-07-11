# -*- coding: utf-8 -*-
from .http import HttpChannel


class Ding(HttpChannel):
    """钉钉消息通知
    https://developers.dingtalk.com/document/app/custom-robot-access?spm=ding_open_doc.document.0.0.6d9d28e1QcCPII#topic-2026027
    """

    payload_kind = "json"
    provider_name = "ding"
    success_fields = {"errcode": {0}}
    success_log_message = "`钉钉` send successfully"

    @property
    def api_url(self):
        return (
            "https://oapi.dingtalk.com/robot/send"
            f"?access_token={self.resolve_config_value('token')}"
        )

    @property
    def headers(self):
        return {"Content-Type": "application/json"}

    def build_api_body(self, content, title=None):
        title = title or "消息提醒"
        api_body = {
            "msgtype": "markdown",
            "markdown": {"title": title, "text": content},
            "at": {},
        }
        if self.config.at_all:
            api_body["at"]["isAtAll"] = self.config.at_all
        if self.config.at_mobiles:
            api_body["at"]["atMobiles"] = self.config.at_mobiles
        if self.config.at_user_ids:
            api_body["at"]["atUserIds"] = self.config.at_user_ids
        return api_body

    def build_request_payload(self, content, title=None):
        return self.build_api_body(content, title)
