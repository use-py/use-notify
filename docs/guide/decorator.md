# use-notify Decorator Guide

`@notify(...)` sends success and failure notifications around a wrapped function
without changing the function's normal return value or business exception.

## Basic Usage

```python
from use_notify import notify, set_default_notify_instance, useNotify, useNotifyChannel

default_notify = useNotify(
    [
        useNotifyChannel.Console(),
    ]
)
set_default_notify_instance(default_notify)


@notify(title="数据同步")
def sync_data():
    return "ok"
```

The default notify instance is scoped to the current execution context. Different
threads or async tasks can set different defaults without overwriting each other.

## Explicit Instance

```python
from use_notify import notify, useNotify, useNotifyChannel

notify_instance = useNotify(
    [
        useNotifyChannel.Bark({"token": "your_bark_token"}),
    ]
)


@notify(notify_instance=notify_instance, title="任务通知")
def task():
    return "done"
```

An explicit `notify_instance` takes priority over the context default.

## Success-Only Or Error-Only

```python
@notify(notify_on_success=True, notify_on_error=False)
def success_only():
    return "ok"


@notify(notify_on_success=False, notify_on_error=True)
def error_only():
    raise RuntimeError("boom")
```

`notify_on_success=False` and `notify_on_error=False` cannot be used together.

## Message Templates

```python
@notify(
    title="ETL Job",
    success_template="{function_name} finished in {execution_time:.2f}s",
    error_template="{function_name} failed: {error_message}",
    include_args=True,
    include_result=True,
)
def run_job(batch_id):
    return {"batch_id": batch_id, "status": "ok"}
```

Available template variables include:

- `function_name`
- `execution_time`
- `error_message`
- `start_time`
- `end_time`
- `current_time`
- `args`, `kwargs`, `args_str`, and `kwargs_str` when `include_args=True`
- `result` and `result_str` when a result exists

Long serialized values are truncated to keep notification content compact.

## Async Functions

```python
@notify(title="异步任务")
async def async_task():
    return "async-ok"
```

Async functions use each channel's `send_async(...)` method through
`publish_async(...)`.

## Timeout And Retry Overrides

```python
@notify(
    timeout=3.0,
    max_retries=2,
    retry_delay=0.5,
    retry_backoff=2.0,
    retriable_exceptions=(TimeoutError,),
)
def job():
    return "ok"
```

Decorator retry arguments apply only to that call site and do not mutate the
source `useNotify` instance.

`timeout` applies to notification delivery, not to the wrapped business function.
For sync functions, timed-out delivery is best-effort: the wrapped function
returns quickly, but Python cannot safely kill a running sync send, so the send
may finish later. `use-notify` bounds that background work to a small worker pool.

## Failure Behavior

Notification failures inside the decorator are logged and do not replace the
wrapped function's behavior:

- If the wrapped function succeeds, its original result is returned.
- If the wrapped function raises, the original business exception is re-raised.
- If notification delivery fails, that failure is logged.

Use `useNotify().publish(...)` directly when callers must handle notification
delivery failures as part of their own control flow.
