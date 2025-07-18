### 一个简单可扩展的异步消息通知库

<a href="https://pypi.org/project/use-notify" target="_blank">
    <img src="https://img.shields.io/pypi/v/use-notify.svg" alt="Package version">
</a>

<a href="https://pypi.org/project/use-notify" target="_blank">
    <img src="https://img.shields.io/pypi/pyversions/use-notify.svg" alt="Supported Python versions">
</a>

#### 安装

> pip install use-notify

#### 使用

```python
from use_notify import useNotify, useNotifyChannel

notify = useNotify()
notify.add(
    # 添加多个通知渠道
    useNotifyChannel.Bark({"token": "xxxxxx"}),
    useNotifyChannel.Ding({
        "token": "xxxxx",
        "at_all": True
    })
)

notify.publish(title="消息标题", content="消息正文")

```

#### 装饰器使用（推荐）

使用 `@notify` 装饰器可以自动为函数执行发送通知：

```python
from use_notify import useNotify, useNotifyChannel, notify, set_default_notify_instance

# 创建并设置全局默认通知实例
default_notify = useNotify()
default_notify.add(
    useNotifyChannel.Bark({"token": "your_bark_token"}),
    useNotifyChannel.Ding({"token": "your_ding_token"})
)
set_default_notify_instance(default_notify)

# 现在可以直接使用装饰器，无需传递 notify_instance
@notify()
def data_processing():
    # 数据处理逻辑
    return "数据处理完成"

@notify(title="重要任务")
def important_task():
    # 重要任务逻辑
    return "重要任务完成"

@notify(notify_on_error=True, notify_on_success=False)
def risky_operation():
    # 只在出错时通知
    if some_condition:
        raise Exception("操作失败")
    return "操作成功"

# 异步函数支持
@notify()
async def async_task():
    await some_async_operation()
    return "异步任务完成"
```

**装饰器特性：**
- ✅ 自动发送成功/失败通知
- ✅ 支持同步和异步函数
- ✅ 可配置通知条件和自定义消息
- ✅ 全局默认实例，简化使用
- ✅ 执行上下文信息收集

> 📖 **详细文档**: [装饰器完整使用指南](docs/decorator.md)

#### 支持的消息通知渠道列表

- Wechat(企微)
- Ding(钉钉)
- Bark
- Email
- Chanify
- Pushdeer
- Pushover
- FeiShu(飞书)
- Ntfy

#### 自己开发消息通知

```python
from use_notify import useNotifyChannel


class Custom(useNotifyChannel.BaseChannel):
    """自定义消息通知"""

    def send(self, *args, **kwargs):
        ...

    async def send_async(self, *args, **kwargs):
        ...
```

#### 更多示例

- [基础使用示例](example/demo.py)
- [装饰器演示](example/decorator_demo.py)
- [装饰器真实场景应用](example/decorator_real_usage.py)
- [全局默认实例使用](example/decorator_default_instance.py)
- [配置文件使用](example/from_setting.py)

#### 文档

- [装饰器完整使用指南](docs/decorator.md) - 详细的装饰器功能说明和最佳实践

#### 特性

- 🚀 **简单易用**: 几行代码即可集成多种通知渠道
- 🔄 **异步支持**: 完整的异步/同步双模式支持
- 🎯 **装饰器模式**: 使用 `@notify` 装饰器自动化通知
- 🔧 **高度可扩展**: 轻松添加自定义通知渠道
- 📱 **多渠道支持**: 支持微信、钉钉、Bark、邮件等多种通知方式
- ⚙️ **灵活配置**: 支持条件通知、自定义模板、全局默认实例等高级功能
