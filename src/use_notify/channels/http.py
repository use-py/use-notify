import logging
from abc import abstractmethod

import httpx

from .base import BaseChannel
from .utils import validate_business_response

logger = logging.getLogger(__name__)


class HttpChannel(BaseChannel):
    request_method = "POST"
    payload_kind = "json"
    success_fields = None
    provider_name = None
    success_log_message = None

    @abstractmethod
    def build_request_payload(self, content, title=None):
        raise NotImplementedError

    def send(self, content, title=None):
        payload = self.build_request_payload(content, title)
        with httpx.Client() as client:
            response = self._send_request(client, payload)
            self._handle_response(response)
        self._log_success()

    async def send_async(self, content, title=None):
        payload = self.build_request_payload(content, title)
        async with httpx.AsyncClient() as client:
            response = await self._send_request_async(client, payload)
            self._handle_response(response)
        self._log_success()

    def _send_request(self, client, payload):
        if self.request_method == "POST":
            return client.post(self.api_url, headers=self.headers, **self._payload_kwargs(payload))
        if self.request_method == "GET":
            return client.get(self.api_url, headers=self.headers, **self._payload_kwargs(payload))
        raise ValueError(f"Unsupported HTTP method: {self.request_method}")

    async def _send_request_async(self, client, payload):
        if self.request_method == "POST":
            return await client.post(
                self.api_url,
                headers=self.headers,
                **self._payload_kwargs(payload),
            )
        if self.request_method == "GET":
            return await client.get(
                self.api_url,
                headers=self.headers,
                **self._payload_kwargs(payload),
            )
        raise ValueError(f"Unsupported HTTP method: {self.request_method}")

    def _payload_kwargs(self, payload):
        if self.payload_kind == "json":
            return {"json": payload}
        if self.payload_kind == "data":
            return {"data": payload}
        if self.payload_kind == "params":
            return {"params": payload}
        raise ValueError(f"Unsupported HTTP payload kind: {self.payload_kind}")

    def _handle_response(self, response):
        response.raise_for_status()
        if self.success_fields:
            validate_business_response(response, self.provider_name, self.success_fields)

    def _log_success(self):
        if self.success_log_message:
            logger.debug(self.success_log_message)
