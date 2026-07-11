# HTTP Channel Transport Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Share sync and async HTTP transport logic across HTTP-backed notification channels without changing the public API.

**Architecture:** Add `HttpChannel`, a focused base class that owns `send()` and `send_async()` for HTTP-backed channels. Provider classes keep URL, headers, payload building, success validation settings, and success log text.

**Tech Stack:** Python 3.8+, `httpx.Client`, `httpx.AsyncClient`, pytest, pytest-asyncio, unittest.mock.

---

## File Structure

- Create: `src/use_notify/channels/http.py`
  - Owns shared HTTP request dispatch for sync and async paths.
  - Converts `payload_kind` into the right `httpx` keyword.
  - Calls `raise_for_status()` and optional `validate_business_response(...)`.
- Modify: `src/use_notify/channels/bark.py`
  - Inherit `HttpChannel`.
  - Keep `_prepare_payload(...)` for compatibility with existing tests.
- Modify: `src/use_notify/channels/chanify.py`
  - Inherit `HttpChannel`.
  - Keep `build_api_body(...)`.
- Modify: `src/use_notify/channels/ding.py`
  - Inherit `HttpChannel`.
  - Keep `build_api_body(...)`.
- Modify: `src/use_notify/channels/feishu.py`
  - Inherit `HttpChannel`.
  - Keep `build_api_body(...)`.
- Modify: `src/use_notify/channels/wechat.py`
  - Inherit `HttpChannel`.
  - Keep `build_api_body(...)` and existing argument order.
- Modify: `src/use_notify/channels/pushover.py`
  - Inherit `HttpChannel`.
  - Keep `build_api_body(...)`.
- Modify: `src/use_notify/channels/pushdeer.py`
  - Inherit `HttpChannel`.
  - Keep `_prepare_params(...)` and token validation in `api_url`.
- Modify: `src/use_notify/channels/ntfy.py`
  - Inherit `HttpChannel`.
  - Keep `_prepare_payload(...)` and topic validation.
- Modify: `tests/test_channels.py`
  - Add direct tests for the new base class unsupported method and unsupported payload kind.
  - Existing channel tests continue to verify request shapes.

## Task 1: Add HTTP Transport Base

**Files:**
- Create: `src/use_notify/channels/http.py`
- Modify: `tests/test_channels.py`

- [ ] **Step 1: Write tests for unsupported transport configuration**

Add these imports near the top of `tests/test_channels.py`:

```python
from use_notify.channels.http import HttpChannel
```

Add these test helper classes and tests after `_credential_provider(...)`:

```python
class UnsupportedMethodChannel(HttpChannel):
    request_method = "PATCH"

    @property
    def api_url(self):
        return "https://example.com"

    @property
    def headers(self):
        return {}

    def build_request_payload(self, content, title=None):
        return {"message": content}


class UnsupportedPayloadChannel(HttpChannel):
    payload_kind = "body"

    @property
    def api_url(self):
        return "https://example.com"

    @property
    def headers(self):
        return {}

    def build_request_payload(self, content, title=None):
        return {"message": content}


def test_http_channel_rejects_unsupported_method():
    channel = UnsupportedMethodChannel({})

    with pytest.raises(ValueError, match="Unsupported HTTP method"):
        channel.send("hello")


def test_http_channel_rejects_unsupported_payload_kind():
    channel = UnsupportedPayloadChannel({})

    with pytest.raises(ValueError, match="Unsupported HTTP payload kind"):
        channel.send("hello")
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```bash
uv run --group dev pytest tests/test_channels.py::test_http_channel_rejects_unsupported_method tests/test_channels.py::test_http_channel_rejects_unsupported_payload_kind -q
```

Expected: import failure because `use_notify.channels.http` does not exist.

- [ ] **Step 3: Create `HttpChannel`**

Create `src/use_notify/channels/http.py`:

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run:

```bash
uv run --group dev pytest tests/test_channels.py::test_http_channel_rejects_unsupported_method tests/test_channels.py::test_http_channel_rejects_unsupported_payload_kind -q
```

Expected: `2 passed`.

- [ ] **Step 5: Commit Task 1**

Run:

```bash
git add src/use_notify/channels/http.py tests/test_channels.py
git commit -m "refactor: add shared http channel transport"
```

## Task 2: Migrate POST JSON Channels

**Files:**
- Modify: `src/use_notify/channels/bark.py`
- Modify: `src/use_notify/channels/ding.py`
- Modify: `src/use_notify/channels/feishu.py`
- Modify: `src/use_notify/channels/wechat.py`
- Modify: `src/use_notify/channels/ntfy.py`

- [ ] **Step 1: Migrate Bark**

Replace `import httpx`, `from .base import BaseChannel`, and `from .utils import validate_business_response` with:

```python
from .http import HttpChannel
```

Change the class definition and add class attributes:

```python
class Bark(HttpChannel):
    """Bark app 消息通知"""

    payload_kind = "json"
    provider_name = "bark"
    success_fields = {"code": {200}}
    success_log_message = "`bark` send successfully"
```

Add:

```python
    def build_request_payload(self, content, title=None):
        return self._prepare_payload(content, title)
```

Remove the custom `send(...)` and `send_async(...)` methods.

- [ ] **Step 2: Migrate Ding**

Replace HTTP imports with:

```python
from .http import HttpChannel
```

Use:

```python
class Ding(HttpChannel):
    """钉钉消息通知
    https://developers.dingtalk.com/document/app/custom-robot-access?spm=ding_open_doc.document.0.0.6d9d28e1QcCPII#topic-2026027
    """

    payload_kind = "json"
    provider_name = "ding"
    success_fields = {"errcode": {0}}
    success_log_message = "`钉钉` send successfully"
```

Add:

```python
    def build_request_payload(self, content, title=None):
        return self.build_api_body(content, title)
```

Remove custom `send(...)` and `send_async(...)`.

- [ ] **Step 3: Migrate Feishu**

Replace HTTP imports with:

```python
from .http import HttpChannel
```

Use:

```python
class Feishu(HttpChannel):
    """飞书消息通知
    https://open.feishu.cn/document/client-docs/bot-v3/add-custom-bot?lang=zh-CN
    """

    payload_kind = "json"
    provider_name = "feishu"
    success_fields = {"code": {0}}
    success_log_message = "`飞书` send successfully"
```

Add:

```python
    def build_request_payload(self, content, title=None):
        return self.build_api_body(content, title)
```

Remove custom `send(...)` and `send_async(...)`.

- [ ] **Step 4: Migrate WeChat**

Replace HTTP imports with:

```python
from .http import HttpChannel
```

Use:

```python
class WeChat(HttpChannel):
    """企业微信消息通知"""

    payload_kind = "json"
    provider_name = "wechat"
    success_fields = {"errcode": {0}}
    success_log_message = "`WeChat` send successfully"
```

Add:

```python
    def build_request_payload(self, content, title=None):
        return self.build_api_body(title, content)
```

Remove custom `send(...)` and `send_async(...)`.

- [ ] **Step 5: Migrate Ntfy**

Replace `import httpx` and `from .base import BaseChannel` with:

```python
from .http import HttpChannel
```

Use:

```python
class Ntfy(HttpChannel):
    """Ntfy.sh 通知渠道"""

    payload_kind = "json"
    success_log_message = "`ntfy` send successfully"
```

Add:

```python
    def build_request_payload(self, content, title=None):
        return self._prepare_payload(content, title)
```

Remove custom `send(...)` and `send_async(...)`. Do not add `success_fields`; Ntfy only checks HTTP status.

- [ ] **Step 6: Run focused tests**

Run:

```bash
uv run --group dev pytest tests/test_channels.py -q
```

Expected: all channel tests pass.

- [ ] **Step 7: Commit Task 2**

Run:

```bash
git add src/use_notify/channels/bark.py src/use_notify/channels/ding.py src/use_notify/channels/feishu.py src/use_notify/channels/wechat.py src/use_notify/channels/ntfy.py
git commit -m "refactor: migrate json http channels"
```

## Task 3: Migrate POST Data and GET Params Channels

**Files:**
- Modify: `src/use_notify/channels/chanify.py`
- Modify: `src/use_notify/channels/pushover.py`
- Modify: `src/use_notify/channels/pushdeer.py`

- [ ] **Step 1: Migrate Chanify**

Replace HTTP imports with:

```python
from .http import HttpChannel
```

Use:

```python
class Chanify(HttpChannel):
    """chanify 消息通知"""

    payload_kind = "data"
    provider_name = "chanify"
    success_fields = {"res": {0}, "code": {0}}
    success_log_message = "`chanify` send successfully"
```

Add:

```python
    def build_request_payload(self, content, title=None):
        return self.build_api_body(content, title)
```

Remove custom `send(...)` and `send_async(...)`.

- [ ] **Step 2: Migrate PushOver**

Replace HTTP imports with:

```python
from .http import HttpChannel
```

Use:

```python
class PushOver(HttpChannel):
    """pushover app 消息通知"""

    payload_kind = "data"
    provider_name = "pushover"
    success_fields = {"status": {1}}
    success_log_message = "`pushover` send successfully"
```

Add:

```python
    def build_request_payload(self, content, title=None):
        return self.build_api_body(content, title)
```

Remove custom `send(...)` and `send_async(...)`.

- [ ] **Step 3: Migrate PushDeer**

Replace HTTP imports with:

```python
from .http import HttpChannel
```

Use:

```python
class PushDeer(HttpChannel):
    """pushdeer app 消息通知

    支持三种消息类型:
    - text: 纯文本消息
    - image: 图片消息
    - markdown: Markdown格式消息 (默认)

    配置参数:
    - token: PushDeer的pushkey
    - base_url: 可选，自建PushDeer服务的URL，默认为"https://api2.pushdeer.com"
    - type: 可选，消息类型，可选值为text、markdown、image，默认为markdown
    """

    request_method = "GET"
    payload_kind = "params"
    provider_name = "pushdeer"
    success_fields = {"code": {0}}
    success_log_message = "`pushdeer` send message successfully"
```

Add:

```python
    def build_request_payload(self, content, title=None):
        return self._prepare_params(content, title)
```

Remove custom `send(...)` and `send_async(...)`.

- [ ] **Step 4: Run focused tests**

Run:

```bash
uv run --group dev pytest tests/test_channels.py -q
```

Expected: all channel tests pass.

- [ ] **Step 5: Commit Task 3**

Run:

```bash
git add src/use_notify/channels/chanify.py src/use_notify/channels/pushover.py src/use_notify/channels/pushdeer.py
git commit -m "refactor: migrate form and params http channels"
```

## Task 4: Full Verification and Documentation

**Files:**
- Modify: `docs/superpowers/plans/2026-07-11-http-channel-transport.md` only if checkbox tracking is updated.

- [ ] **Step 1: Run lint**

Run:

```bash
make lint
```

Expected: isort, black, and flake8 all pass.

- [ ] **Step 2: Run tests**

Run:

```bash
make test
```

Expected: `126 passed` plus any new tests added in Task 1.

- [ ] **Step 3: Run coverage**

Run:

```bash
make coverage
```

Expected: total coverage remains at or above 95%.

- [ ] **Step 4: Inspect final diff**

Run:

```bash
git diff --stat origin/main...HEAD
git diff origin/main...HEAD -- src/use_notify/channels tests/test_channels.py
```

Expected: diff shows the new HTTP transport and migrated channel classes without public API changes.

- [ ] **Step 5: Push branch and open PR**

Run:

```bash
git push -u origin refactor-http-channel-transport
gh pr create --base main --head refactor-http-channel-transport --title "Refactor HTTP channels to share transport logic" --body "<body that closes #59 and lists verification>"
```

Expected: PR created and linked to Issue #59.
