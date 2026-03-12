# useNotify 类

`useNotify` 是 `use_notify.notification.Notify` 的导出别名，本质上是一个支持多渠道发送、失败重试和配置构造的发布器。

## 导入

```python
from use_notify import NotificationPublishError, RetryConfig, useNotify, useNotifyChannel
```

## 构造函数

```python
notify = useNotify(
    channels=None,
    max_retries=0,
    retry_delay=0.0,
    retry_backoff=1.0,
    retriable_exceptions=(TimeoutError, ConnectionError, OSError),
)
```

参数说明：

- `channels`: 初始渠道列表，可省略
- `max_retries`: 每个渠道的最大重试次数，默认 `0`
- `retry_delay`: 首次重试前等待秒数，默认 `0.0`
- `retry_backoff`: 每次重试后延迟的倍数，默认 `1.0`
- `retriable_exceptions`: 额外视为可重试的异常类型元组

```python
notify = useNotify([
    useNotifyChannel.Bark({"token": "bark-token"}),
    useNotifyChannel.Console(),
])
```

## 常用方法

### `add(*channels)`

向当前实例追加一个或多个渠道。

```python
notify = useNotify()
notify.add(
    useNotifyChannel.Bark({"token": "bark-token"}),
    useNotifyChannel.Ding({"token": "ding-token"}),
)
```

说明：

- 不会清空已有渠道
- 内部会复制状态，避免影响正在进行中的发送任务

### `publish(*args, **kwargs)`

同步发送通知。最常见的调用方式是传 `title` 和 `content` 两个关键字参数：

```python
notify.publish(title="系统告警", content="CPU 使用率超过 90%")
```

也可以直接传位置参数：

```python
notify.publish("CPU 使用率超过 90%", title="系统告警")
```

行为说明：

- 会依次尝试所有渠道
- 某个渠道失败不会阻止其他渠道继续尝试
- 只要存在失败，发送结束后仍会抛异常
- 单个渠道失败时，直接抛该渠道的原始异常
- 多个渠道失败时，抛 `NotificationPublishError`

### `publish_async(*args, **kwargs)`

异步并发发送通知：

```python
await notify.publish_async(title="异步消息", content="任务处理完成")
```

行为与 `publish()` 一致，但会使用 `asyncio.gather()` 并发调度各渠道的 `send_async()`。

### `configure_retry(...)`

更新当前实例后续发送所使用的重试策略，并返回实例本身，方便链式调用。

```python
notify.configure_retry(
    max_retries=2,
    retry_delay=0.5,
    retry_backoff=2.0,
    retriable_exceptions=(TimeoutError, RuntimeError),
)
```

### `from_settings(settings)`

根据配置字典批量构造渠道。渠道名按大小写不敏感匹配。

```python
notify = useNotify.from_settings(
    {
        "bArk": {"token": "bark-token"},
        "wecom": {"token": "wechat-token"},
    }
)
```

说明：

- `wecom` 会映射到 `WeCom` / `WeChat`
- 未知渠道名会抛 `ValueError`

## 属性

### `channels`

当前已配置渠道的只读快照，类型是 `tuple`。

```python
for channel in notify.channels:
    print(channel.__class__.__name__)
```

### `retry_config`

当前实例生效中的重试配置，类型是 `RetryConfig`。

```python
print(notify.retry_config.max_retries)
```

## 重试语义

默认情况下，以下情况会被视为可重试：

- `TimeoutError`
- `ConnectionError`
- `OSError`
- `httpx.RequestError`
- HTTP 状态码为 `408`、`429` 或 `5xx`
- SMTP `4xx` 响应错误

以下情况默认不重试：

- `httpx.HTTPStatusError` 但状态码不是 `408`、`429`、`5xx`
- `smtplib.SMTPAuthenticationError`
- 你自己抛出的普通业务异常，如 `ValueError`

## 错误处理

### 单渠道失败

如果只有一个渠道失败，会直接重新抛出该异常：

```python
try:
    notify.publish(title="测试", content="内容")
except Exception as error:
    print(type(error).__name__, error)
```

### 多渠道失败

如果多个渠道都失败，会抛出 `NotificationPublishError`：

```python
try:
    notify.publish(title="测试", content="内容")
except NotificationPublishError as error:
    for channel_name, channel_error in error.failures:
        print(channel_name, channel_error)
```

## 完整示例

```python
from use_notify import NotificationPublishError, useNotify, useNotifyChannel

notify = useNotify(
    max_retries=1,
    retry_delay=0.5,
)
notify.add(
    useNotifyChannel.Console(),
    useNotifyChannel.Ntfy({"topic": "alerts"}),
)

try:
    notify.publish(title="部署完成", content="生产环境发布成功")
except NotificationPublishError as error:
    print(error.failures)
```
