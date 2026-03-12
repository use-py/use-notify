# 异常说明

当前版本的 `use-notify` 并没有单独的 `use_notify.exceptions` 模块。
常见异常主要分成两类：发布器异常和装饰器配置异常。

## 发布器异常

### `NotificationPublishError`

当多个渠道都发生失败时，`useNotify.publish()` / `useNotify.publish_async()` 会抛出 `NotificationPublishError`。

```python
from use_notify import NotificationPublishError, useNotify, useNotifyChannel

notify = useNotify([
    useNotifyChannel.Console(),
    useNotifyChannel.Ntfy({"topic": "alerts"}),
])

try:
    notify.publish(title="测试", content="内容")
except NotificationPublishError as error:
    for channel_name, channel_error in error.failures:
        print(channel_name, channel_error)
```

属性：

- `failures`: `list[tuple[str, Exception]]`

说明：

- 列表中的每一项都是 `(渠道类名, 原始异常对象)`
- 如果只有一个渠道失败，不会包装成 `NotificationPublishError`，而是直接重新抛出原始异常

## 重试配置错误

### `RetryConfig`

`RetryConfig` 不是异常类，而是描述重试策略的数据类。
如果传入非法值，会抛 `ValueError`。

```python
from use_notify import RetryConfig

RetryConfig(max_retries=1, retry_delay=0.5)

try:
    RetryConfig(retriable_exceptions=("invalid",))
except ValueError as error:
    print(error)
```

## 装饰器异常

这些异常定义在 `use_notify.decorator` 下：

```python
from use_notify.decorator import (
    NotifyConfigError,
    NotifyDecoratorError,
    NotifySendError,
)
```

### `NotifyDecoratorError`

装饰器相关异常的基类。

### `NotifyConfigError`

装饰器参数校验失败时抛出，例如：

- `notify_instance` 不是 `useNotify` 实例
- `timeout` 不是正数
- `max_retries` 小于 `0`
- `retriable_exceptions` 里包含了非异常类型
- `notify_on_success` 和 `notify_on_error` 同时为 `False`

```python
from use_notify.decorator import NotifyConfigError
from use_notify import notify

try:
    @notify(max_retries=-1)
    def task():
        return "ok"
except NotifyConfigError as error:
    print(error)
```

### `NotifySendError`

这个类型目前定义在装饰器模块中，但默认实现并不会主动抛出它。
当前内置的通知发送器在发送失败时默认只记录日志，不会让通知错误覆盖业务函数结果。

因此，对使用者来说，最重要的实际行为是：

- 业务函数成功时，通知失败不会影响返回值
- 业务函数失败时，原始业务异常会继续向外抛出

## 建议的捕获方式

### 发布器

```python
try:
    notify.publish(title="测试", content="内容")
except NotificationPublishError as error:
    ...
except Exception as error:
    ...
```

### 装饰器

```python
@notify()
def run():
    raise RuntimeError("boom")

try:
    run()
except RuntimeError:
    # 捕获业务异常，而不是通知异常
    ...
```
