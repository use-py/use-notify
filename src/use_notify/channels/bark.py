from .http import HttpChannel


class Bark(HttpChannel):
    """Bark app 消息通知"""

    payload_kind = "json"
    provider_name = "bark"
    success_fields = {"code": {200}}
    success_log_message = "`bark` send successfully"

    @property
    def api_url(self):
        # Check if base_url exists in config, otherwise use default
        if self.config.base_url:
            base_url = self.config.base_url.rstrip("/")
        else:
            base_url = "https://api.day.app"

        return f"{base_url}/{self.resolve_config_value('token')}"

    @property
    def headers(self):
        return {"Content-Type": "application/json; charset=utf-8"}

    def _prepare_payload(self, content, title=None):
        payload = {
            "body": content,
        }

        if title:
            payload["title"] = title

        # Optional parameters from config
        for param in ["badge", "sound", "icon", "group", "url"]:
            if param in self.config and getattr(self.config, param) is not None:
                payload[param] = getattr(self.config, param)

        return payload

    def build_request_payload(self, content, title=None):
        return self._prepare_payload(content, title)
