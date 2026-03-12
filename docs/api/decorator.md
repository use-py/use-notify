# 装饰器 API

`@notify` 用来在函数执行成功或失败后自动发送通知，支持同步函数和异步函数。

## 导入

```python
from use_notify import notify

# 或者
from use_notify.decorator import notify
```

## 函数签名

```python
@notify(
    notify_instance=None,
    title=None,
    success_template=None,
    error_template=None,
    notify_on_success=True,
    notify_on_error=True,
    include_args=False,
    include_result=False,
    timeout=None,
    max_retries=None,
    retry_delay=None,
    retry_backoff=None,
    retriable_exceptions=None,
)
```

## 参数说明

### `notify_instance`

指定本次装饰器使用的通知实例。

- 类型：`useNotify | None`
- 默认值：`None`

如果没有传入：

1. 先尝试读取当前执行上下文中的默认实例
2. 如果仍然没有，内部会创建一个空的 `useNotify()` 并记录 warning

```python
from use_notify import useNotify, useNotifyChannel, notify

custom_notify = useNotify([
    useNotifyChannel.Console(),
])

@notify(notify_instance=custom_notify)
def run_job():
    return "ok"
```

### `title`

通知标题。可以是固定字符串，也可以使用模板变量。

```python
@notify(title="任务完成")
def task():
    return "ok"

@notify(title="函数 {function_name} 执行完成")
def another_task():
    return "ok"
```

### `success_template` / `error_template`

分别定义成功和失败通知的内容模板。

```python
@notify(
    success_template="✅ {function_name} 成功，耗时 {execution_time:.2f} 秒",
    error_template="❌ {function_name} 失败: {error_message}",
)
def sync_data():
    return "done"
```

### `notify_on_success` / `notify_on_error`

控制成功或失败时是否发送通知。

```python
@notify(notify_on_success=False, notify_on_error=True)
def error_only():
    ...
```

注意：这两个参数不能同时为 `False`。

### `include_args` / `include_result`

用于把参数和返回值放进模板上下文。

```python
@notify(include_args=True, include_result=True)
def process(order_id):
    return {"order_id": order_id, "status": "ok"}
```

### `timeout`

通知发送超时时间，单位是秒。

这个超时作用于“发送通知”本身，不是业务函数执行超时。

- 同步通知：内部通过线程池等待 `publish()`，超时后记录日志，不阻塞业务函数返回
- 异步通知：内部通过 `asyncio.wait_for()` 包裹通知发送

```python
@notify(timeout=3.0)
def sync_task():
    return "ok"
```

### 重试参数

这些参数会覆盖当前通知实例上的重试配置，但不会修改原实例本身：

- `max_retries`
- `retry_delay`
- `retry_backoff`
- `retriable_exceptions`

```python
@notify(
    max_retries=2,
    retry_delay=0.5,
    retry_backoff=2.0,
    retriable_exceptions=(TimeoutError,),
)
def task_with_retry():
    return "ok"
```

## 默认实例函数

可以使用以下函数配置“当前执行上下文”的默认通知实例：

```python
from use_notify import (
    clear_default_notify_instance,
    get_default_notify_instance,
    set_default_notify_instance,
    useNotify,
    useNotifyChannel,
)

notify_instance = useNotify([
    useNotifyChannel.Console(),
])

set_default_notify_instance(notify_instance)
print(get_default_notify_instance())
clear_default_notify_instance()
```

说明：

- 默认实例按线程/异步任务隔离
- 装饰器在函数真正被调用时解析默认实例，不是在定义装饰器时固定
- 显式传入的 `notify_instance` 优先级更高

## 模板变量

模板里可用的上下文包括：

| 变量 | 说明 |
|------|------|
| `function_name` | 函数名 |
| `args` | 位置参数元组 |
| `kwargs` | 关键字参数字典 |
| `result` | 返回值 |
| `error_message` | 异常消息 |
| `error_type` | 异常类型名 |
| `execution_time` | 函数执行耗时 |
| `start_time` | 开始时间 |
| `end_time` | 结束时间 |
| `current_time` | 格式化通知时的当前时间 |

## 行为说明

### 业务函数成功时

- 原函数返回值保持不变
- 如果开启了成功通知，会尝试发送通知
- 即使通知发送失败，也不会破坏原函数返回

### 业务函数抛错时

- 原始异常会被重新抛出
- 如果开启了失败通知，会先尝试发送失败通知
- 通知发送失败只会记录日志，不会覆盖原始业务异常

## 示例

### 同步函数

```python
@notify(
    title="订单同步",
    success_template="✅ {function_name} 完成，结果: {result}",
    error_template="❌ {function_name} 失败: {error_message}",
    include_result=True,
)
def sync_order(order_id):
    return {"order_id": order_id, "status": "done"}
```

### 异步函数

```python
import asyncio

@notify(title="异步任务", timeout=2.0)
async def async_task():
    await asyncio.sleep(0.1)
    return "ok"
```

### 使用默认实例

```python
from use_notify import notify, set_default_notify_instance, useNotify, useNotifyChannel

default_notify = useNotify([
    useNotifyChannel.Console(),
])
set_default_notify_instance(default_notify)

@notify()
def run():
    return "ok"
```
