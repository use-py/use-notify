# HTTP Channel Transport Refactor Design

Date: 2026-07-11
Issue: https://github.com/use-py/use-notify/issues/59

## Goal

Reduce duplicated sync and async HTTP send logic across HTTP-backed notification channels while keeping the public API unchanged.

Users must keep calling:

```python
channel.send(content, title=None)
await channel.send_async(content, title=None)

notify.publish(title="...", content="...")
await notify.publish_async(title="...", content="...")
```

The refactor should make channel implementations smaller and easier to audit without changing request payloads, dynamic credential behavior, provider response validation, or exception behavior.

## Non-Goals

- Do not merge sync and async public methods into a single method.
- Do not change `Publisher` retry semantics.
- Do not change `Email`; it uses SMTP and already runs sync SMTP work in an executor for async sends.
- Do not change `Console`; it is not HTTP-backed and has different output text for sync and async sends.
- Do not add provider-specific OAuth refresh, background credential refresh, or credential persistence.

## Current Problem

The HTTP-backed channels repeat this pattern:

1. Build request payload from `content`, `title`, and config.
2. Open `httpx.Client` or `httpx.AsyncClient`.
3. Send `GET` or `POST`.
4. Call `response.raise_for_status()`.
5. Optionally call `validate_business_response(...)`.
6. Write a provider-specific success log message.

The duplicated flow exists in:

- Bark
- Chanify
- Ding
- Feishu
- WeChat / WeCom
- PushDeer
- PushOver
- Ntfy

## Recommended Architecture

Add a shared HTTP channel base class:

```python
class HttpChannel(BaseChannel):
    request_method = "POST"
    payload_kind = "json"
    success_fields = None
    provider_name = None
    success_log_message = None

    def build_request_payload(self, content, title=None):
        ...

    def send(self, content, title=None):
        ...

    async def send_async(self, content, title=None):
        ...
```

The base class owns the transport workflow. Subclasses provide provider-specific data:

- `api_url`
- `headers`
- `request_method`
- `payload_kind`
- `success_fields`
- `provider_name`
- `success_log_message`
- `build_request_payload(...)`

Supported `payload_kind` values:

- `json`: pass payload as `json=...`
- `data`: pass payload as `data=...`
- `params`: pass payload as `params=...`

Supported request methods for this refactor:

- `POST`
- `GET`

If a subclass configures an unsupported method or payload kind, the base class should raise `ValueError`. This fails fast during development instead of silently sending the wrong request.

## Channel Migration Map

| Channel | Method | Payload Kind | Success Fields |
| --- | --- | --- | --- |
| Bark | POST | json | `{"code": {200}}` |
| Chanify | POST | data | `{"res": {0}, "code": {0}}` |
| Ding | POST | json | `{"errcode": {0}}` |
| Feishu | POST | json | `{"code": {0}}` |
| WeChat / WeCom | POST | json | `{"errcode": {0}}` |
| PushOver | POST | data | `{"status": {1}}` |
| PushDeer | GET | params | `{"code": {0}}` |
| Ntfy | POST | json | `None` |

Ntfy currently only checks HTTP status. It should keep that behavior.

## Data Flow

Sync send:

```text
send(content, title)
  -> build_request_payload(content, title)
  -> _send_http_request(payload)
  -> response.raise_for_status()
  -> validate_business_response if configured
  -> success log
```

Async send:

```text
send_async(content, title)
  -> build_request_payload(content, title)
  -> await _send_http_request_async(payload)
  -> response.raise_for_status()
  -> validate_business_response if configured
  -> success log
```

Dynamic credentials remain in the channel-specific `api_url` or payload builders through `resolve_config_value(...)`.

## Error Handling

- Preserve `httpx` HTTP status behavior by continuing to call `raise_for_status()`.
- Preserve provider business response behavior by continuing to call `validate_business_response(...)` with the same provider names and success fields.
- Preserve current `ValueError` behavior from channel-specific config checks such as missing PushDeer token and missing Ntfy topic.
- New `ValueError` cases are limited to impossible subclass configuration errors, such as unsupported HTTP method or payload kind.

## Testing

Existing tests should continue to prove behavior:

- Request method, URL, headers, and body shape for every migrated channel.
- Dynamic credential callables resolve at request-building time.
- Provider business response errors are still raised.
- Sync and async paths both send the same data.
- Ntfy still only relies on HTTP status.

Run:

```bash
make lint
make test
make coverage
```

Coverage must remain above the configured 95% threshold.

## Rollout Plan

1. Add `HttpChannel` with tests covering payload dispatch and unsupported configuration.
2. Migrate one representative JSON POST channel first, then the rest.
3. Migrate data POST channels.
4. Migrate GET params channel.
5. Run the full suite and review the diff for unchanged public behavior.

## Open Decisions

None. The design intentionally keeps the public API unchanged and avoids changing non-HTTP channels.
