# 通知渠道配置

use-notify 支持多种通知渠道，每个渠道都有其特定的配置参数。本指南将详细介绍各个渠道的配置方法。

## 支持的通知渠道

### Bark（iOS 推送）

Bark 是一个 iOS 推送通知应用。

```python
from use_notify import useNotify, useNotifyChannel

notify = useNotify()
notify.add(useNotifyChannel.Bark({
    "token": "your_bark_token",  # 必需
    "server": "https://api.day.app",  # 可选，默认官方服务器
    "sound": "default",  # 可选，通知声音
    "group": "myapp",  # 可选，通知分组
    "icon": "https://example.com/icon.png"  # 可选，自定义图标
}))
```

**配置参数：**
- `token` (必需): Bark 应用中的设备令牌
- `server` (可选): Bark 服务器地址，默认为官方服务器
- `sound` (可选): 通知声音，如 "default", "bell", "silence" 等
- `group` (可选): 通知分组名称
- `icon` (可选): 自定义通知图标 URL

### 钉钉（DingTalk）

钉钉群机器人通知。

```python
notify.add(useNotifyChannel.Ding({
    "token": "your_dingtalk_token",  # 必需
    "secret": "your_secret",  # 可选，加签密钥
    "at_all": False,  # 可选，是否@所有人
    "at_mobiles": ["13800138000"],  # 可选，@指定手机号
    "at_user_ids": ["user123"]  # 可选，@指定用户ID
}))
```

**配置参数：**
- `token` (必需): 钉钉机器人的 Webhook Token
- `secret` (可选): 加签密钥，用于安全验证
- `at_all` (可选): 是否@所有人，默认 False
- `at_mobiles` (可选): @指定手机号列表
- `at_user_ids` (可选): @指定用户ID列表

### 企业微信（WeChat Work）

企业微信群机器人通知。

```python
notify.add(useNotifyChannel.WeChat({
    "token": "your_key",  # 必需
    "mentioned_list": ["@all"],  # 可选，@成员列表
    "mentioned_mobile_list": ["13800138000"]  # 可选，@手机号列表
}))
```

**配置参数：**
- `token` (必需): 企业微信机器人的 Webhook Token
- `mentioned_list` (可选): @成员列表，使用 "@all" 可@所有人
- `mentioned_mobile_list` (可选): @手机号列表

### 邮件（Email）

SMTP 邮件通知。

```python
notify.add(useNotifyChannel.Email({
    "smtp_server": "smtp.gmail.com",  # 必需
    "smtp_port": 587,  # 必需
    "username": "your_email@gmail.com",  # 必需
    "password": "your_password",  # 必需
    "to_emails": ["recipient@example.com"],  # 必需
    "from_email": "your_email@gmail.com",  # 可选，默认使用username
    "use_tls": True,  # 可选，是否使用TLS
    "use_ssl": False  # 可选，是否使用SSL
}))
```

**配置参数：**
- `smtp_server` (必需): SMTP 服务器地址
- `smtp_port` (必需): SMTP 服务器端口
- `username` (必需): 邮箱用户名
- `password` (必需): 邮箱密码或应用密码
- `to_emails` (必需): 收件人邮箱列表
- `from_email` (可选): 发件人邮箱，默认使用 username
- `use_tls` (可选): 是否使用 TLS 加密，默认 True
- `use_ssl` (可选): 是否使用 SSL 加密，默认 False

### Pushover

Pushover 推送服务。

```python
notify.add(useNotifyChannel.Pushover({
    "token": "your_app_token",  # 必需
    "user": "your_user_key",  # 必需
    "device": "your_device",  # 可选
    "priority": 0,  # 可选，优先级 (-2 到 2)
    "sound": "default"  # 可选，通知声音
}))
```

**配置参数：**
- `token` (必需): Pushover 应用令牌
- `user` (必需): Pushover 用户密钥
- `device` (可选): 特定设备名称
- `priority` (可选): 消息优先级，范围 -2 到 2
- `sound` (可选): 通知声音

### Pushdeer

Pushdeer 推送服务。

```python
notify.add(useNotifyChannel.Pushdeer({
    "token": "your_pushdeer_token",  # 必需
    "server": "https://api2.pushdeer.com"  # 可选，默认官方服务器
}))
```

**配置参数：**
- `token` (必需): Pushdeer 设备令牌
- `server` (可选): Pushdeer 服务器地址

### Chanify

Chanify 推送服务。

```python
notify.add(useNotifyChannel.Chanify({
    "token": "your_chanify_token",  # 必需
    "server": "https://api.chanify.net"  # 可选，默认官方服务器
}))
```

**配置参数：**
- `token` (必需): Chanify 设备令牌
- `server` (可选): Chanify 服务器地址

## 多渠道配置

### 添加多个渠道

```python
from use_notify import useNotify, useNotifyChannel

notify = useNotify()

# 一次添加多个渠道
notify.add(
    useNotifyChannel.Bark({"token": "bark_token"}),
    useNotifyChannel.Ding({"token": "ding_token"}),
    useNotifyChannel.Email({
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
        "username": "user@gmail.com",
        "password": "password",
        "to_emails": ["recipient@example.com"]
    })
)

# 或者分别添加
notify.add(useNotifyChannel.Bark({"token": "bark_token"}))
notify.add(useNotifyChannel.Ding({"token": "ding_token"}))
```

### 不同场景使用不同渠道

```python
# 创建不同用途的通知实例

# 日常通知 - 使用轻量级渠道
daily_notify = useNotify()
daily_notify.add(useNotifyChannel.Bark({"token": "bark_token"}))

# 重要警报 - 使用多个渠道确保送达
alert_notify = useNotify()
alert_notify.add(
    useNotifyChannel.Ding({"token": "ding_token", "at_all": True}),
    useNotifyChannel.Email({
        "smtp_server": "smtp.company.com",
        "smtp_port": 587,
        "username": "alerts@company.com",
        "password": "password",
        "to_emails": ["admin@company.com", "ops@company.com"]
    }),
    useNotifyChannel.Pushover({
        "token": "pushover_token",
        "user": "admin_user",
        "priority": 2  # 高优先级
    })
)

# 在装饰器中使用不同实例
@notify(notify_instance=daily_notify)
def routine_task():
    return "日常任务完成"

@notify(notify_instance=alert_notify, title="系统警报")
def critical_check():
    return "关键检查完成"
```

## 自定义通知渠道

如果内置渠道不满足需求，可以创建自定义通知渠道：

```python
from use_notify.channels import BaseChannel
import requests

class CustomChannel(BaseChannel):
    """自定义通知渠道"""
    
    def __init__(self, config):
        super().__init__()
        self.api_url = config.get("api_url")
        self.api_key = config.get("api_key")
    
    def send(self, title, content, **kwargs):
        """同步发送通知"""
        try:
            response = requests.post(
                self.api_url,
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={"title": title, "message": content}
            )
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"发送通知失败: {e}")
            return False
    
    async def send_async(self, title, content, **kwargs):
        """异步发送通知"""
        import aiohttp
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.api_url,
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json={"title": title, "message": content}
                ) as response:
                    response.raise_for_status()
                    return True
        except Exception as e:
            print(f"发送通知失败: {e}")
            return False

# 使用自定义渠道
notify = useNotify()
notify.add(CustomChannel({
    "api_url": "https://api.example.com/notify",
    "api_key": "your_api_key"
}))
```

## 配置最佳实践

### 1. 环境变量管理

```python
import os
from use_notify import useNotify, useNotifyChannel

notify = useNotify()

# 使用环境变量管理敏感信息
notify.add(useNotifyChannel.Bark({
    "token": os.getenv("BARK_TOKEN")
}))

notify.add(useNotifyChannel.Ding({
    "token": os.getenv("DING_TOKEN"),
    "secret": os.getenv("DING_SECRET")
}))

notify.add(useNotifyChannel.Email({
    "smtp_server": os.getenv("SMTP_SERVER", "smtp.gmail.com"),
    "smtp_port": int(os.getenv("SMTP_PORT", "587")),
    "username": os.getenv("EMAIL_USERNAME"),
    "password": os.getenv("EMAIL_PASSWORD"),
    "to_emails": os.getenv("EMAIL_RECIPIENTS", "").split(",")
}))
```

### 2. 配置文件管理

```python
import json
from use_notify import useNotify, useNotifyChannel

# 从配置文件加载
with open("notify_config.json", "r") as f:
    config = json.load(f)

notify = useNotify()

# 根据配置动态添加渠道
for channel_config in config["channels"]:
    channel_type = channel_config["type"]
    channel_params = channel_config["params"]
    
    if channel_type == "bark":
        notify.add(useNotifyChannel.Bark(channel_params))
    elif channel_type == "ding":
        notify.add(useNotifyChannel.Ding(channel_params))
    elif channel_type == "email":
        notify.add(useNotifyChannel.Email(channel_params))
```

配置文件示例 (`notify_config.json`):

```json
{
  "channels": [
    {
      "type": "bark",
      "params": {
        "token": "your_bark_token",
        "sound": "default"
      }
    },
    {
      "type": "ding",
      "params": {
        "token": "your_ding_token",
        "at_all": false
      }
    },
    {
      "type": "email",
      "params": {
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
        "username": "your_email@gmail.com",
        "password": "your_password",
        "to_emails": ["recipient@example.com"]
      }
    }
  ]
}
```

### 3. 错误处理和重试

```python
from use_notify import useNotify, useNotifyChannel
import time

class ReliableNotify:
    def __init__(self):
        self.notify = useNotify()
        self.setup_channels()
    
    def setup_channels(self):
        # 添加多个备用渠道
        self.notify.add(
            useNotifyChannel.Bark({"token": os.getenv("BARK_TOKEN")}),
            useNotifyChannel.Ding({"token": os.getenv("DING_TOKEN")}),
            useNotifyChannel.Email({
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "username": os.getenv("EMAIL_USERNAME"),
                "password": os.getenv("EMAIL_PASSWORD"),
                "to_emails": [os.getenv("EMAIL_RECIPIENT")]
            })
        )
    
    def send_with_retry(self, title, content, max_retries=3):
        for attempt in range(max_retries):
            try:
                self.notify.publish(title=title, content=content)
                return True
            except Exception as e:
                print(f"发送失败 (尝试 {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # 指数退避
        return False

# 使用可靠的通知服务
reliable_notify = ReliableNotify()
reliable_notify.send_with_retry("重要通知", "这是一条重要消息")
```

### 4. 测试配置

```python
def test_notification_channels():
    """测试所有配置的通知渠道"""
    notify = useNotify()
    
    # 添加所有渠道
    channels = [
        ("Bark", useNotifyChannel.Bark({"token": os.getenv("BARK_TOKEN")})),
        ("钉钉", useNotifyChannel.Ding({"token": os.getenv("DING_TOKEN")})),
        ("邮件", useNotifyChannel.Email({
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "username": os.getenv("EMAIL_USERNAME"),
            "password": os.getenv("EMAIL_PASSWORD"),
            "to_emails": [os.getenv("EMAIL_RECIPIENT")]
        }))
    ]
    
    for name, channel in channels:
        test_notify = useNotify()
        test_notify.add(channel)
        
        try:
            test_notify.publish(
                title=f"{name} 测试通知",
                content=f"这是来自 {name} 渠道的测试消息"
            )
            print(f"✅ {name} 渠道测试成功")
        except Exception as e:
            print(f"❌ {name} 渠道测试失败: {e}")

if __name__ == "__main__":
    test_notification_channels()
```
