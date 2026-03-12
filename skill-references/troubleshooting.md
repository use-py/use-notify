# Troubleshooting

## Default-instance behavior

- `set_default_notify_instance()` stores the default instance in the current execution context.
- Different threads or async tasks can hold different default instances.
- If `@notify()` is used without an explicit instance and no default has been set, the decorator creates an empty `useNotify()` and logs a warning.

## Publisher error behavior

Calling `notify.publish(...)` or `await notify.publish_async(...)` behaves like this:

- If every configured channel succeeds, nothing is returned.
- If one channel fails, the original channel exception is re-raised.
- If multiple channels fail, `NotificationPublishError` is raised with a `.failures` list.

```python
from use_notify import NotificationPublishError

try:
    notify.publish(title="测试", content="内容")
except NotificationPublishError as error:
    for channel_name, channel_error in error.failures:
        print(channel_name, channel_error)
```

## Decorator error behavior

- Decorated business functions still return their normal result when notification sending fails.
- If the business function itself raises, that original business exception is re-raised.
- Notification failures inside the decorator are logged and do not replace the business exception.

This matters when users expect `@notify(...)` to fail closed. It currently fails open.

## Retry behavior

`useNotify` supports instance-level retries via constructor arguments or `configure_retry(...)`.
`@notify(...)` can also override retries per call site without mutating the original notify instance.

Default retriable categories include:

- `TimeoutError`
- `ConnectionError`
- `OSError`
- `httpx.RequestError`
- HTTP `408`, `429`, and any `5xx`
- SMTP `4xx`

Non-retriable examples include:

- regular `ValueError`
- `smtplib.SMTPAuthenticationError`
- HTTP status errors outside `408`, `429`, and `5xx`

## Timeout behavior

- Decorator `timeout` applies to notification delivery, not to the wrapped business function.
- Sync delivery uses a short-lived thread pool to avoid blocking the caller forever.
- Async delivery uses `asyncio.wait_for(...)`.

## Validation pitfalls

- `notify_on_success=False` and `notify_on_error=False` together are rejected.
- `max_retries` must be `>= 0`.
- `retry_delay` must be `>= 0`.
- `retry_backoff` must be `> 0`.
- `retriable_exceptions` must contain exception types, not strings or instances.
- `Email` requires `server`, `port`, `username`, `password`, and `from_email` during initialization.

## Current public exports

```python
from use_notify import (
    NotificationPublishError,
    RetryConfig,
    notify,
    useNotify,
    useNotifyChannel,
    set_default_notify_instance,
    get_default_notify_instance,
    clear_default_notify_instance,
)
```
