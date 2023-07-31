### 一个简单可扩展的异步消息通知库

<a href="https://pypi.org/project/usepy-plugin-notify" target="_blank">
    <img src="https://img.shields.io/pypi/v/usepy-plugin-notify.svg" alt="Package version">
</a>

<a href="https://pypi.org/project/usepy-plugin-notify" target="_blank">
    <img src="https://img.shields.io/pypi/pyversions/usepy-plugin-notify.svg" alt="Supported Python versions">
</a>

#### 安装

> pip install usepy-plugin-notify

#### 使用

```python
from usepy.plugin import useNotify, useNotifyChannel

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

#### 支持的消息通知渠道列表

- Wechat
- Ding
- Bark
- Email
- Chanify
- Pushdeer
- Pushover

#### 自己开发消息通知

```python
from usepy.plugin import useNotifyChannel


class Custom(useNotifyChannel.BaseChannel):
    """自定义消息通知"""

    def send(self, *args, **kwargs):
        ...

    async def send_async(self, *args, **kwargs):
        ...
```
