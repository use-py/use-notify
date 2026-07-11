from .http import HttpChannel


class Chanify(HttpChannel):
    """chanify 消息通知"""

    payload_kind = "data"
    provider_name = "chanify"
    success_fields = {"res": {0}, "code": {0}}
    success_log_message = "`chanify` send successfully"

    @property
    def api_url(self):
        # Check if base_url exists in config, otherwise use default
        if self.config.base_url:
            base_url = self.config.base_url.rstrip("/")
        else:
            base_url = "https://api.chanify.net"

        return f"{base_url}/v1/sender/{self.resolve_config_value('token')}"

    @property
    def headers(self):
        return {"Content-Type": "application/x-www-form-urlencoded"}

    @staticmethod
    def build_api_body(content, title=None):
        text = f"{title}\n{content}" if title else content
        return {"text": text}

    def build_request_payload(self, content, title=None):
        return self.build_api_body(content, title)
