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
# if you use usepy, also can use `usepy.plugin`
# from usepy.plugin import useNotify, useNotifyChannel

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

#### Loguru 日志上报集成

支持通过 `logger.report()` 方法实现日志上报功能：

```python
from loguru import logger
from use_notify import setup_loguru_reporter
from typing import TYPE_CHECKING

# 为了更好的类型检查支持
if TYPE_CHECKING:
    from use_notify.loguru_types import ExtendedLogger
    logger = logger  # type: ExtendedLogger

# 配置通知渠道
settings = {
    "BARK": {"token": "your_bark_token"},
    "WECHAT": {"token": "your_wechat_token"},
}

# 设置日志上报器（ERROR级别及以上会触发上报）
setup_loguru_reporter(settings=settings, level="ERROR")

# 现在可以使用 logger.report() 进行上报
logger.report("这是一条需要上报的错误消息")

# 指定级别和额外信息
logger.report(
    "系统出现异常", 
    level="CRITICAL",
    服务器="web-01",
    错误代码="E001"
)
```

详细使用说明请参考 [LOGURU_INTEGRATION.md](LOGURU_INTEGRATION.md)

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
from use_notify import useNotifyChannel


class Custom(useNotifyChannel.BaseChannel):
    """自定义消息通知"""

    def send(self, *args, **kwargs):
        ...

    async def send_async(self, *args, **kwargs):
        ...
```
