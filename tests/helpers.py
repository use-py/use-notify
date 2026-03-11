import httpx

from use_notify.channels.base import BaseChannel


class RecordingChannel(BaseChannel):
    def __init__(self, sync_failures=None, async_failures=None):
        super().__init__({})
        self.sync_failures = list(sync_failures or [])
        self.async_failures = list(async_failures or [])
        self.sync_messages = []
        self.async_messages = []

    def send(self, content, title=None):
        self.sync_messages.append({"content": content, "title": title})
        if self.sync_failures:
            raise self.sync_failures.pop(0)

    async def send_async(self, content, title=None):
        self.async_messages.append({"content": content, "title": title})
        if self.async_failures:
            raise self.async_failures.pop(0)


def make_http_status_error(status_code, method="POST", url="https://example.com/test"):
    request = httpx.Request(method, url)
    response = httpx.Response(status_code, request=request)
    return httpx.HTTPStatusError(
        f"status {status_code}",
        request=request,
        response=response,
    )
