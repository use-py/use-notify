# API 参考

`use-notify` 当前对外暴露的核心能力可以分成 4 组：

- `useNotify`: 通知发布器，负责管理渠道、发送消息和重试策略
- `useNotifyChannel`: 内置通知渠道集合
- `@notify`: 为同步/异步函数自动发送成功或失败通知
- 默认实例函数: `set_default_notify_instance()`、`get_default_notify_instance()`、`clear_default_notify_instance()`

## 推荐导入方式

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

## 核心对象

### `useNotify`

`useNotify` 是 `Notify` 的导出别名，用来管理多个渠道并统一发送消息。

常用能力：

- `add(*channels)`: 添加一个或多个渠道
- `publish(...)`: 同步发送通知
- `publish_async(...)`: 异步发送通知
- `configure_retry(...)`: 更新后续发送的重试策略
- `from_settings(settings)`: 从配置字典创建实例

详细说明见 [useNotify 类](./usenotify)。

### `useNotifyChannel`

`useNotifyChannel` 模块包含当前内置渠道：

- `Bark`
- `Chanify`
- `Console`
- `Ding`
- `Email`
- `Feishu`
- `Ntfy`
- `PushDeer`
- `PushOver`
- `WeChat`
- `WeCom`，这是 `WeChat` 的兼容别名

详细说明见 [通知渠道 API](./channels)。

### `@notify`

装饰器支持同步函数和异步函数，并允许按调用粒度覆盖标题、模板、超时和重试参数。

```python
from use_notify import notify

@notify(title="任务完成")
def run_job():
    return "ok"
```

详细说明见 [装饰器 API](./decorator)。

## 默认实例函数

默认实例不是进程级“全局单例”，而是按当前执行上下文隔离的默认通知实例。
这意味着不同线程、不同异步任务可以各自设置自己的默认实例，互不干扰。

```python
from use_notify import useNotify, useNotifyChannel, set_default_notify_instance

notify_instance = useNotify([
    useNotifyChannel.Console(),
])

set_default_notify_instance(notify_instance)
```

## 错误与重试

- `RetryConfig`: 描述发布器重试策略的数据类
- `NotificationPublishError`: 多个渠道都出现失败时的聚合异常，包含 `.failures`
- 单个渠道失败时，`publish()` / `publish_async()` 会直接重新抛出该渠道的原始异常
- 装饰器内部默认不会把通知发送失败再抛给业务函数，而是记录日志并继续返回业务结果

详细说明见 [异常说明](./exceptions)。

## 下一步

- 需要看发布器行为时，优先读 [useNotify 类](./usenotify)
- 需要看参数、模板变量和超时/重试时，读 [装饰器 API](./decorator)
- 需要看各渠道配置项时，读 [通知渠道 API](./channels)
