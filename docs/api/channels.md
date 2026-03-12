# 通知渠道 API

`useNotifyChannel` 提供了当前内置的所有通知渠道实现。

## 导入

```python
from use_notify import useNotifyChannel

# 精确到某个渠道也可以这样导入
from use_notify.channels import Bark, Console, Ding, Email
```

当前可用类名：

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

## 基础接口

所有渠道都继承自 `BaseChannel`，方法签名统一为：

```python
class BaseChannel:
    def __init__(self, config: dict):
        ...

    def send(self, content, title=None):
        ...

    async def send_async(self, content, title=None):
        ...
```

注意：

- 用户层通常调用 `notify.publish(title="标题", content="内容")`
- 渠道实现层收到的方法签名是 `send(content, title=None)`

## 内置渠道

### `Bark`

```python
useNotifyChannel.Bark(
    {
        "token": "your_bark_token",
        "base_url": "https://api.day.app",
        "badge": 1,
        "sound": "bell",
        "icon": "https://example.com/icon.png",
        "group": "ops",
        "url": "https://example.com",
    }
)
```

常用配置：

- `token`，必填
- `base_url`，可选
- `badge`、`sound`、`icon`、`group`、`url`，可选

### `Chanify`

```python
useNotifyChannel.Chanify(
    {
        "token": "your_chanify_token",
        "base_url": "https://api.chanify.net",
    }
)
```

常用配置：

- `token`，必填
- `base_url`，可选

### `Console`

```python
useNotifyChannel.Console()
```

无必填配置，适合本地演示和测试。

### `Ding`

```python
useNotifyChannel.Ding(
    {
        "token": "your_ding_token",
        "at_all": False,
        "at_mobiles": ["13800000000"],
        "at_user_ids": ["user-1"],
    }
)
```

常用配置：

- `token`，必填
- `at_all`、`at_mobiles`、`at_user_ids`，可选

### `Email`

```python
useNotifyChannel.Email(
    {
        "server": "smtp.gmail.com",
        "port": 465,
        "username": "bot@example.com",
        "password": "app-password",
        "from_email": "bot@example.com",
        "to_emails": ["ops@example.com"],
    }
)
```

初始化时会校验：

- `server`
- `port`
- `username`
- `password`
- `from_email`

实际发送时通常还需要提供：

- `to_emails`

### `Feishu`

```python
useNotifyChannel.Feishu(
    {
        "token": "your_feishu_token",
        "at_all": True,
        "at_user_ids": ["ou_xxx"],
    }
)
```

常用配置：

- `token`，必填
- `at_all`、`at_user_ids`，可选

### `Ntfy`

```python
useNotifyChannel.Ntfy(
    {
        "topic": "alerts",
        "base_url": "https://ntfy.sh",
        "priority": 4,
        "tags": ["warning"],
        "click": "https://example.com",
        "attach": "https://example.com/file.txt",
        "actions": [
            {"action": "view", "label": "Open", "url": "https://example.com"}
        ],
    }
)
```

常用配置：

- `topic`，必填
- `base_url`、`priority`、`tags`、`click`、`attach`、`actions`，可选

### `PushDeer`

```python
useNotifyChannel.PushDeer(
    {
        "token": "your_pushkey",
        "base_url": "https://api2.pushdeer.com",
        "type": "markdown",
    }
)
```

常用配置：

- `token`，必填
- `base_url`，可选
- `type`，可选，支持 `text`、`markdown`、`image`

### `PushOver`

```python
useNotifyChannel.PushOver(
    {
        "token": "your_app_token",
        "user": "your_user_key",
    }
)
```

常用配置：

- `token`，必填
- `user`，必填

### `WeChat` / `WeCom`

```python
useNotifyChannel.WeChat(
    {
        "token": "your_wechat_key",
        "mentioned_list": ["@all"],
        "mentioned_mobile_list": ["13800000000"],
    }
)
```

常用配置：

- `token`，必填
- `mentioned_list`、`mentioned_mobile_list`，可选

## 自定义渠道

如果内置渠道不够用，可以继承 `BaseChannel`：

```python
from use_notify.channels import BaseChannel
import httpx


class CustomChannel(BaseChannel):
    def __init__(self, config):
        super().__init__(config)
        self.api_url = self.config.api_url
        self.api_key = self.config.api_key

    def send(self, content, title=None):
        response = httpx.post(
            self.api_url,
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={"title": title, "message": content},
        )
        response.raise_for_status()

    async def send_async(self, content, title=None):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.api_url,
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={"title": title, "message": content},
            )
            response.raise_for_status()
```

## 示例

```python
from use_notify import useNotify, useNotifyChannel

notify = useNotify()
notify.add(
    useNotifyChannel.Console(),
    useNotifyChannel.Ntfy({"topic": "alerts"}),
)

notify.publish(title="部署完成", content="生产环境发布成功")
```
