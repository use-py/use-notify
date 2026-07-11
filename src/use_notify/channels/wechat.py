# -*- coding: utf-8 -*-
from .http import HttpChannel


class WeChat(HttpChannel):
    """企业微信消息通知"""

    payload_kind = "json"
    provider_name = "wechat"
    success_fields = {"errcode": {0}}
    success_log_message = "`WeChat` send successfully"

    @property
    def api_url(self):
        return (
            "https://qyapi.weixin.qq.com/cgi-bin/webhook/send"
            f"?key={self.resolve_config_value('token')}"
        )

    @property
    def headers(self):
        return {"Content-Type": "application/json"}

    def build_api_body(self, title, content):
        if title:
            content = f"## {title}\n\n{content}"
        api_body = {"markdown": {"content": content}, "msgtype": "markdown"}

        if self.config.mentioned_list:
            api_body["markdown"]["mentioned_list"] = self.config.mentioned_list
        if self.config.mentioned_mobile_list:
            api_body["markdown"]["mentioned_mobile_list"] = self.config.mentioned_mobile_list

        return api_body

    def build_request_payload(self, content, title=None):
        return self.build_api_body(title, content)
