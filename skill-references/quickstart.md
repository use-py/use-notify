# Quickstart

## Install

```bash
pip install use-notify
```

## Basic publisher usage

```python
from use_notify import useNotify, useNotifyChannel

notify = useNotify()
notify.add(
    useNotifyChannel.Console(),
    useNotifyChannel.Ntfy({"topic": "alerts"}),
)

notify.publish(title="部署完成", content="生产环境发布成功")
```

## Decorator usage

Use the decorator when the user wants automatic success or failure notifications around a function.

```python
from use_notify import notify, set_default_notify_instance, useNotify, useNotifyChannel

default_notify = useNotify([
    useNotifyChannel.Console(),
])
set_default_notify_instance(default_notify)


@notify(title="数据同步")
def sync_data():
    return "ok"
```

## Error-only decorator

```python
from use_notify import notify


@notify(notify_on_success=False, notify_on_error=True)
def risky_job():
    raise RuntimeError("boom")
```

## Decorator with timeout and retry overrides

```python
from use_notify import notify


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

## Build from settings

Channel names are matched case-insensitively.

```python
from use_notify import useNotify

notify = useNotify.from_settings(
    {
        "bark": {"token": "bark-token"},
        "wecom": {"token": "wechat-token"},
    }
)
```

## Custom channel

```python
from use_notify.channels import BaseChannel


class CustomChannel(BaseChannel):
    def send(self, content, title=None):
        print(title, content)

    async def send_async(self, content, title=None):
        self.send(content, title)
```

## When to choose each pattern

- Function wrapping, cron tasks, or business operations: prefer `@notify`.
- One-off sends from scripts or services: prefer `useNotify().publish(...)`.
- Existing config objects or env-derived dicts: prefer `useNotify.from_settings(...)`.
