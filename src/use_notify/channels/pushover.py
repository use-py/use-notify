from .http import HttpChannel


class PushOver(HttpChannel):
    """pushover app 消息通知"""

    payload_kind = "data"
    provider_name = "pushover"
    success_fields = {"status": {1}}
    success_log_message = "`pushover` send successfully"

    @property
    def api_url(self):
        return "https://api.pushover.net/1/messages.json"

    @property
    def headers(self):
        return {"Content-Type": "application/x-www-form-urlencoded"}

    def build_api_body(self, content, title=None):
        return {
            "token": self.resolve_config_value("token"),
            "user": self.resolve_config_value("user"),
            "title": title,
            "message": content,
        }

    def build_request_payload(self, content, title=None):
        return self.build_api_body(content, title)
