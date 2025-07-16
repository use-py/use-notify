# API 参考

use-notify 提供了简洁而强大的 API，支持多种通知渠道和使用方式。本节详细介绍所有可用的 API。

## 核心 API

### useNotify 类

主要的通知管理类，用于管理通知渠道和发送通知。

```python
from use_notify import useNotify

notify = useNotify()
```

**主要方法：**
- `add(*channels)` - 添加通知渠道
- `publish(title, content, **kwargs)` - 发送同步通知
- `publish_async(title, content, **kwargs)` - 发送异步通知
- `remove_all()` - 移除所有通知渠道

### useNotifyChannel 模块

包含所有内置的通知渠道实现。

```python
from use_notify import useNotifyChannel

# 可用的通知渠道
channels = [
    useNotifyChannel.Bark,
    useNotifyChannel.Ding,
    useNotifyChannel.WeChat,
    useNotifyChannel.Email,
    useNotifyChannel.Pushover,
    useNotifyChannel.Pushdeer,
    useNotifyChannel.Chanify
]
```

### 装饰器 API

用于函数和方法的通知装饰器。

```python
from use_notify import notify

@notify(title="任务完成", content="任务执行成功")
def my_task():
    return "完成"
```

**装饰器参数：**
- `notify_instance` - 通知实例
- `title` - 通知标题
- `content` - 通知内容
- `content_template` - 内容模板
- `condition` - 通知条件
- `include_args` - 是否包含函数参数
- `include_result` - 是否包含函数结果
- `timeout` - 超时设置

### 全局默认实例 API

管理全局默认通知实例的函数。

```python
from use_notify import (
    set_default_notify_instance,
    get_default_notify_instance,
    clear_default_notify_instance
)

# 设置全局默认实例
set_default_notify_instance(notify)

# 获取全局默认实例
default_notify = get_default_notify_instance()

# 清除全局默认实例
clear_default_notify_instance()
```

## 通知渠道 API

### 基础渠道接口

所有通知渠道都实现了以下接口：

```python
class BaseChannel:
    def send(self, title: str, content: str, **kwargs) -> bool:
        """同步发送通知"""
        pass
    
    async def send_async(self, title: str, content: str, **kwargs) -> bool:
        """异步发送通知"""
        pass
```

### Bark 渠道

iOS Bark 推送通知。

```python
from use_notify import useNotifyChannel

bark = useNotifyChannel.Bark({
    "token": "your_bark_token",
    "server": "https://api.day.app",  # 可选
    "sound": "default",  # 可选
    "group": "myapp",  # 可选
    "icon": "https://example.com/icon.png"  # 可选
})
```

**配置参数：**
- `token` (必需): Bark 设备令牌
- `server` (可选): Bark 服务器地址
- `sound` (可选): 通知声音
- `group` (可选): 通知分组
- `icon` (可选): 自定义图标 URL

### 钉钉渠道

钉钉群机器人通知。

```python
ding = useNotifyChannel.Ding({
    "token": "your_dingtalk_token",
    "secret": "your_secret",  # 可选
    "at_all": False,  # 可选
    "at_mobiles": ["13800138000"],  # 可选
    "at_user_ids": ["user123"]  # 可选
})
```

**配置参数：**
- `token` (必需): 钉钉机器人 Webhook Token
- `secret` (可选): 加签密钥
- `at_all` (可选): 是否@所有人
- `at_mobiles` (可选): @指定手机号列表
- `at_user_ids` (可选): @指定用户ID列表

### 企业微信渠道

企业微信群机器人通知。

```python
wechat = useNotifyChannel.WeChat({
    "webhook_url": "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=your_key",
    "mentioned_list": ["@all"],  # 可选
    "mentioned_mobile_list": ["13800138000"]  # 可选
})
```

**配置参数：**
- `webhook_url` (必需): 企业微信机器人 Webhook URL
- `mentioned_list` (可选): @成员列表
- `mentioned_mobile_list` (可选): @手机号列表

### 邮件渠道

SMTP 邮件通知。

```python
email = useNotifyChannel.Email({
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "username": "your_email@gmail.com",
    "password": "your_password",
    "to_emails": ["recipient@example.com"],
    "from_email": "your_email@gmail.com",  # 可选
    "use_tls": True,  # 可选
    "use_ssl": False  # 可选
})
```

**配置参数：**
- `smtp_server` (必需): SMTP 服务器地址
- `smtp_port` (必需): SMTP 服务器端口
- `username` (必需): 邮箱用户名
- `password` (必需): 邮箱密码
- `to_emails` (必需): 收件人邮箱列表
- `from_email` (可选): 发件人邮箱
- `use_tls` (可选): 是否使用 TLS
- `use_ssl` (可选): 是否使用 SSL

### Pushover 渠道

Pushover 推送服务。

```python
pushover = useNotifyChannel.Pushover({
    "token": "your_app_token",
    "user": "your_user_key",
    "device": "your_device",  # 可选
    "priority": 0,  # 可选
    "sound": "default"  # 可选
})
```

**配置参数：**
- `token` (必需): Pushover 应用令牌
- `user` (必需): Pushover 用户密钥
- `device` (可选): 特定设备名称
- `priority` (可选): 消息优先级 (-2 到 2)
- `sound` (可选): 通知声音

### Pushdeer 渠道

Pushdeer 推送服务。

```python
pushdeer = useNotifyChannel.Pushdeer({
    "token": "your_pushdeer_token",
    "server": "https://api2.pushdeer.com"  # 可选
})
```

**配置参数：**
- `token` (必需): Pushdeer 设备令牌
- `server` (可选): Pushdeer 服务器地址

### Chanify 渠道

Chanify 推送服务。

```python
chanify = useNotifyChannel.Chanify({
    "token": "your_chanify_token",
    "server": "https://api.chanify.net"  # 可选
})
```

**配置参数：**
- `token` (必需): Chanify 设备令牌
- `server` (可选): Chanify 服务器地址

## 异常类

use-notify 定义了以下异常类：

### NotifyConfigError

配置错误异常，当通知配置不正确时抛出。

```python
from use_notify.exceptions import NotifyConfigError

try:
    notify.add(invalid_channel)
except NotifyConfigError as e:
    print(f"配置错误: {e}")
```

### NotifySendError

发送错误异常，当通知发送失败时抛出。

```python
from use_notify.exceptions import NotifySendError

try:
    notify.publish(title="测试", content="内容")
except NotifySendError as e:
    print(f"发送失败: {e}")
```

## 扩展 API

### 自定义通知渠道

创建自定义通知渠道：

```python
from use_notify.channels import BaseChannel
import requests

class CustomChannel(BaseChannel):
    """自定义通知渠道"""
    
    def __init__(self, config):
        super().__init__()
        self.api_url = config['api_url']
        self.api_key = config['api_key']
    
    def send(self, title, content, **kwargs):
        """同步发送通知"""
        try:
            response = requests.post(
                self.api_url,
                headers={'Authorization': f'Bearer {self.api_key}'},
                json={'title': title, 'message': content}
            )
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"发送失败: {e}")
            return False
    
    async def send_async(self, title, content, **kwargs):
        """异步发送通知"""
        import aiohttp
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.api_url,
                    headers={'Authorization': f'Bearer {self.api_key}'},
                    json={'title': title, 'message': content}
                ) as response:
                    response.raise_for_status()
                    return True
        except Exception as e:
            print(f"发送失败: {e}")
            return False

# 使用自定义渠道
notify = useNotify()
notify.add(CustomChannel({
    'api_url': 'https://api.example.com/notify',
    'api_key': 'your_api_key'
}))
```
