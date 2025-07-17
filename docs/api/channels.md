# 通知渠道 API

`useNotifyChannel` 模块提供了多种内置的通知渠道实现，每个渠道都有特定的配置参数和功能特性。

## 模块导入

```python
from use_notify import useNotifyChannel

# 或者导入特定渠道
from use_notify.channels import BarkChannel, DingChannel, EmailChannel
```

## 基础渠道接口

所有通知渠道都继承自基础接口，提供统一的方法签名：

```python
class BaseChannel:
    def __init__(self, config: dict):
        """初始化渠道配置"""
        pass
    
    def send(self, title: str, content: str, **kwargs) -> bool:
        """同步发送通知"""
        pass
    
    async def send_async(self, title: str, content: str, **kwargs) -> bool:
        """异步发送通知"""
        pass
```

## Bark 渠道

### `useNotifyChannel.Bark(config)`

Bark 是一个专为 iOS 设备设计的推送通知服务。

#### 配置参数

```python
config = {
    "token": "your_bark_token",           # 必需：Bark 设备令牌
    "server": "https://api.day.app",      # 可选：Bark 服务器地址
    "sound": "default",                   # 可选：通知声音
    "icon": "https://example.com/icon.png", # 可选：通知图标
    "group": "MyApp",                     # 可选：通知分组
    "url": "https://example.com"          # 可选：点击通知打开的URL
}

bark = useNotifyChannel.Bark(config)
```

#### 参数说明

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| `token` | str | 是 | - | Bark 应用中的设备令牌 |
| `server` | str | 否 | `https://api.day.app` | Bark 服务器地址 |
| `sound` | str | 否 | `default` | 通知声音名称 |
| `icon` | str | 否 | - | 通知图标 URL |
| `group` | str | 否 | - | 通知分组名称 |
| `url` | str | 否 | - | 点击通知时打开的 URL |

#### 使用示例

```python
from use_notify import useNotify, useNotifyChannel

# 基本配置
bark = useNotifyChannel.Bark({
    "token": "your_bark_token"
})

# 完整配置
bark_full = useNotifyChannel.Bark({
    "token": "your_bark_token",
    "server": "https://api.day.app",
    "sound": "alarm",
    "icon": "https://example.com/icon.png",
    "group": "系统通知",
    "url": "https://example.com/dashboard"
})

notify = useNotify()
notify.add(bark_full)
notify.publish("系统警报", "服务器CPU使用率过高")
```

#### 支持的声音

常用的 Bark 声音选项：
- `default` - 默认声音
- `alarm` - 警报声
- `anticipate` - 期待声
- `bell` - 铃声
- `birdsong` - 鸟鸣声
- `bloom` - 绽放声
- `calypso` - 卡吕普索
- `chime` - 钟声
- `choo` - 火车声
- `descent` - 下降声
- `electronic` - 电子音
- `fanfare` - 号角声
- `glass` - 玻璃声
- `gotosleep` - 睡眠声
- `healthnotification` - 健康通知
- `horn` - 喇叭声
- `ladder` - 阶梯声
- `mailsent` - 邮件发送
- `minuet` - 小步舞曲
- `multiwayinvitation` - 多方邀请
- `newmail` - 新邮件
- `newsflash` - 新闻快报
- `noir` - 黑色电影
- `paymentsuccess` - 支付成功
- `shake` - 震动
- `sherwoodforest` - 舍伍德森林
- `silence` - 静音
- `spell` - 咒语
- `suspense` - 悬疑
- `telegraph` - 电报
- `tiptoes` - 踮脚尖
- `typewriters` - 打字机
- `update` - 更新

## 钉钉渠道

### `useNotifyChannel.Ding(config)`

钉钉群机器人通知渠道，支持文本、Markdown 和 ActionCard 消息类型。

#### 配置参数

```python
config = {
    "token": "your_ding_token",           # 必需：钉钉机器人 Webhook Token
    "secret": "your_ding_secret",         # 可选：钉钉机器人签名密钥
    "msg_type": "text",                   # 可选：消息类型
    "at_mobiles": ["13800138000"],        # 可选：@指定手机号
    "at_all": False                       # 可选：是否@所有人
}

ding = useNotifyChannel.Ding(config)
```

#### 参数说明

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| `token` | str | 是 | - | 钉钉机器人 Webhook Token |
| `secret` | str | 否 | - | 钉钉机器人签名密钥（推荐使用） |
| `msg_type` | str | 否 | `text` | 消息类型：`text`、`markdown`、`actionCard` |
| `at_mobiles` | list | 否 | `[]` | 需要@的手机号列表 |
| `at_all` | bool | 否 | `False` | 是否@所有人 |

#### 使用示例

```python
from use_notify import useNotify, useNotifyChannel

# 基本文本消息
ding_text = useNotifyChannel.Ding({
    "token": "your_ding_token",
    "secret": "your_ding_secret"
})

# Markdown 消息
ding_markdown = useNotifyChannel.Ding({
    "token": "your_ding_token",
    "secret": "your_ding_secret",
    "msg_type": "markdown"
})

# @特定用户
ding_at = useNotifyChannel.Ding({
    "token": "your_ding_token",
    "secret": "your_ding_secret",
    "at_mobiles": ["13800138000", "13900139000"],
    "at_all": False
})

notify = useNotify()
notify.add(ding_markdown)

# 发送 Markdown 格式消息
markdown_content = """
## 系统监控报告

**时间**: 2024-01-01 12:00:00

**状态**: ⚠️ 警告

**详情**:
- CPU 使用率: 85%
- 内存使用率: 78%
- 磁盘使用率: 92%

[查看详细报告](https://example.com/report)
"""

notify.publish("系统监控警报", markdown_content)
```

#### 消息类型

**1. 文本消息 (text)**
```python
ding = useNotifyChannel.Ding({
    "token": "your_token",
    "msg_type": "text"
})
```

**2. Markdown 消息 (markdown)**
```python
ding = useNotifyChannel.Ding({
    "token": "your_token",
    "msg_type": "markdown"
})

# 支持 Markdown 语法
content = """
# 标题
## 二级标题
**粗体文本**
*斜体文本*
[链接](https://example.com)
- 列表项1
- 列表项2
"""
```

**3. ActionCard 消息 (actionCard)**
```python
ding = useNotifyChannel.Ding({
    "token": "your_token",
    "msg_type": "actionCard"
})

# 在发送时提供额外参数
notify.publish(
    title="系统警报",
    content="服务器异常，请及时处理",
    single_title="查看详情",
    single_url="https://example.com/alert"
)
```

## 企业微信渠道

### `useNotifyChannel.WeChat(config)`

企业微信群机器人通知渠道，支持文本、Markdown 和图文消息。

#### 配置参数

```python
config = {
    "token": "your_key",  # 必需
    "mentioned_list": ["@all"],           # 可选：@成员列表
    "mentioned_mobile_list": []           # 可选：@手机号列表
}

wechat = useNotifyChannel.WeChat(config)
```

#### 参数说明

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| `token` | str | 是 | - | 企业微信机器人 Webhook Token |
| `mentioned_list` | list | 否 | `[]` | @成员的用户ID列表，`@all` 表示所有人 |
| `mentioned_mobile_list` | list | 否 | `[]` | @成员的手机号列表 |

#### 使用示例

```python
from use_notify import useNotify, useNotifyChannel

# 基本配置
wechat = useNotifyChannel.WeChat({
    "token": "your_key"
})

notify = useNotify()
notify.add(wechat_md)

# 发送 Markdown 消息
markdown_content = """
## 📊 系统状态报告

> **时间**: <font color="info">2024-01-01 12:00:00</font>
> **状态**: <font color="warning">警告</font>

**服务器指标**:
- CPU: <font color="warning">85%</font>
- 内存: <font color="info">78%</font>
- 磁盘: <font color="warning">92%</font>

[查看详细监控](https://example.com/monitor)
"""

notify.publish("系统监控", markdown_content)
```

## 邮件渠道

### `useNotifyChannel.Email(config)`

电子邮件通知渠道，支持 HTML 和纯文本邮件。

#### 配置参数

```python
config = {
    "smtp_server": "smtp.gmail.com",      # 必需：SMTP 服务器地址
    "smtp_port": 587,                     # 必需：SMTP 端口
    "username": "sender@gmail.com",       # 必需：发送者邮箱
    "password": "your_password",          # 必需：邮箱密码或应用密码
    "to_emails": ["recipient@example.com"], # 必需：收件人列表
    "from_name": "System Notifier",       # 可选：发送者名称
    "use_tls": True,                      # 可选：是否使用 TLS
    "use_ssl": False,                     # 可选：是否使用 SSL
    "cc_emails": [],                      # 可选：抄送列表
    "bcc_emails": []                      # 可选：密送列表
}

email = useNotifyChannel.Email(config)
```

#### 参数说明

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| `smtp_server` | str | 是 | - | SMTP 服务器地址 |
| `smtp_port` | int | 是 | - | SMTP 端口号 |
| `username` | str | 是 | - | 发送者邮箱地址 |
| `password` | str | 是 | - | 邮箱密码或应用专用密码 |
| `to_emails` | list | 是 | - | 收件人邮箱地址列表 |
| `from_name` | str | 否 | `username` | 发送者显示名称 |
| `use_tls` | bool | 否 | `True` | 是否使用 TLS 加密 |
| `use_ssl` | bool | 否 | `False` | 是否使用 SSL 加密 |
| `cc_emails` | list | 否 | `[]` | 抄送邮箱地址列表 |
| `bcc_emails` | list | 否 | `[]` | 密送邮箱地址列表 |

#### 常用邮箱服务器配置

**Gmail**
```python
gmail_config = {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "use_tls": True,
    "username": "your_email@gmail.com",
    "password": "your_app_password",  # 使用应用专用密码
    "to_emails": ["recipient@example.com"]
}
```

**Outlook/Hotmail**
```python
outlook_config = {
    "smtp_server": "smtp-mail.outlook.com",
    "smtp_port": 587,
    "use_tls": True,
    "username": "your_email@outlook.com",
    "password": "your_password",
    "to_emails": ["recipient@example.com"]
}
```

**QQ邮箱**
```python
qq_config = {
    "smtp_server": "smtp.qq.com",
    "smtp_port": 587,
    "use_tls": True,
    "username": "your_email@qq.com",
    "password": "your_authorization_code",  # 使用授权码
    "to_emails": ["recipient@example.com"]
}
```

**163邮箱**
```python
netease_config = {
    "smtp_server": "smtp.163.com",
    "smtp_port": 25,
    "use_tls": False,
    "username": "your_email@163.com",
    "password": "your_authorization_code",  # 使用授权码
    "to_emails": ["recipient@example.com"]
}
```

#### 使用示例

```python
from use_notify import useNotify, useNotifyChannel

# 基本邮件配置
email = useNotifyChannel.Email({
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "username": "sender@gmail.com",
    "password": "your_app_password",
    "to_emails": ["admin@example.com", "ops@example.com"],
    "from_name": "系统监控",
    "cc_emails": ["manager@example.com"]
})

notify = useNotify()
notify.add(email)

# 发送纯文本邮件
notify.publish(
    title="服务器警报",
    content="服务器 web-01 的 CPU 使用率已达到 90%，请及时处理。"
)

# 发送 HTML 邮件
html_content = """
<html>
<body>
    <h2 style="color: #e74c3c;">🚨 系统警报</h2>
    <p><strong>时间</strong>: 2024-01-01 12:00:00</p>
    <p><strong>服务器</strong>: web-01</p>
    <p><strong>问题</strong>: CPU 使用率过高</p>
    
    <table border="1" style="border-collapse: collapse; margin: 20px 0;">
        <tr style="background-color: #f8f9fa;">
            <th style="padding: 10px;">指标</th>
            <th style="padding: 10px;">当前值</th>
            <th style="padding: 10px;">阈值</th>
            <th style="padding: 10px;">状态</th>
        </tr>
        <tr>
            <td style="padding: 10px;">CPU</td>
            <td style="padding: 10px; color: #e74c3c;">90%</td>
            <td style="padding: 10px;">80%</td>
            <td style="padding: 10px; color: #e74c3c;">⚠️ 警告</td>
        </tr>
        <tr>
            <td style="padding: 10px;">内存</td>
            <td style="padding: 10px; color: #f39c12;">75%</td>
            <td style="padding: 10px;">80%</td>
            <td style="padding: 10px; color: #27ae60;">✅ 正常</td>
        </tr>
    </table>
    
    <p>
        <a href="https://monitor.example.com/server/web-01" 
           style="background-color: #3498db; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
           查看详细监控
        </a>
    </p>
</body>
</html>
"""

notify.publish(
    title="系统监控报告",
    content=html_content,
    content_type="html"  # 指定内容类型为 HTML
)
```

## Pushover 渠道

### `useNotifyChannel.Pushover(config)`

Pushover 是一个跨平台的推送通知服务。

#### 配置参数

```python
config = {
    "token": "your_app_token",            # 必需：应用 Token
    "user": "your_user_key",             # 必需：用户密钥
    "device": "your_device_name",        # 可选：设备名称
    "priority": 0,                        # 可选：优先级 (-2 到 2)
    "sound": "pushover",                  # 可选：通知声音
    "url": "https://example.com",        # 可选：补充 URL
    "url_title": "查看详情"               # 可选：URL 标题
}

pushover = useNotifyChannel.Pushover(config)
```

#### 参数说明

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| `token` | str | 是 | - | Pushover 应用 Token |
| `user` | str | 是 | - | Pushover 用户密钥 |
| `device` | str | 否 | - | 特定设备名称 |
| `priority` | int | 否 | `0` | 消息优先级：-2(静音) 到 2(紧急) |
| `sound` | str | 否 | `pushover` | 通知声音名称 |
| `url` | str | 否 | - | 补充 URL |
| `url_title` | str | 否 | - | URL 显示标题 |

#### 优先级说明

- `-2`: 静音通知，不产生声音或振动
- `-1`: 安静通知，不产生声音，但会振动
- `0`: 正常优先级（默认）
- `1`: 高优先级，绕过用户的安静时间
- `2`: 紧急优先级，重复通知直到确认

#### 使用示例

```python
from use_notify import useNotify, useNotifyChannel

# 基本配置
pushover = useNotifyChannel.Pushover({
    "token": "your_app_token",
    "user": "your_user_key"
})

# 高优先级通知
pushover_urgent = useNotifyChannel.Pushover({
    "token": "your_app_token",
    "user": "your_user_key",
    "priority": 2,  # 紧急
    "sound": "siren",
    "url": "https://monitor.example.com",
    "url_title": "查看监控面板"
})

notify = useNotify()
notify.add(pushover_urgent)

notify.publish(
    title="🚨 严重警报",
    content="数据库服务器连接失败，请立即处理！"
)
```

## Pushdeer 渠道

### `useNotifyChannel.Pushdeer(config)`

Pushdeer 是一个开源的推送服务。

#### 配置参数

```python
config = {
    "token": "your_pushdeer_token",       # 必需：Pushdeer Token
    "server": "https://api2.pushdeer.com", # 可选：服务器地址
    "type": "text"                        # 可选：消息类型
}

pushdeer = useNotifyChannel.Pushdeer(config)
```

#### 参数说明

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| `token` | str | 是 | - | Pushdeer 设备 Token |
| `server` | str | 否 | `https://api2.pushdeer.com` | Pushdeer 服务器地址 |
| `type` | str | 否 | `text` | 消息类型：`text` 或 `markdown` |

#### 使用示例

```python
from use_notify import useNotify, useNotifyChannel

# Markdown 消息
pushdeer = useNotifyChannel.Pushdeer({
    "token": "your_pushdeer_token",
    "type": "markdown"
})

notify = useNotify()
notify.add(pushdeer)

# 发送 Markdown 格式通知
markdown_content = """
## 📈 性能报告

**服务器**: web-server-01  
**时间**: 2024-01-01 12:00:00

### 系统指标
- **CPU**: 45% ✅
- **内存**: 67% ⚠️
- **磁盘**: 23% ✅
- **网络**: 正常 ✅

### 应用状态
- **Web服务**: 运行中 ✅
- **数据库**: 运行中 ✅
- **缓存**: 运行中 ✅

[查看详细报告](https://monitor.example.com)
"""

notify.publish("系统性能报告", markdown_content)
```

## Chanify 渠道

### `useNotifyChannel.Chanify(config)`

Chanify 是一个简单的推送通知服务。

#### 配置参数

```python
config = {
    "token": "your_chanify_token",        # 必需：Chanify Token
    "server": "https://api.chanify.net",  # 可选：服务器地址
    "sound": 1,                           # 可选：声音设置
    "priority": 10                        # 可选：优先级
}

chanify = useNotifyChannel.Chanify(config)
```

#### 参数说明

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| `token` | str | 是 | - | Chanify 设备 Token |
| `server` | str | 否 | `https://api.chanify.net` | Chanify 服务器地址 |
| `sound` | int | 否 | `1` | 声音设置：0(静音) 或 1(有声) |
| `priority` | int | 否 | `10` | 消息优先级：1-10 |

#### 使用示例

```python
from use_notify import useNotify, useNotifyChannel

# 高优先级通知
chanify = useNotifyChannel.Chanify({
    "token": "your_chanify_token",
    "sound": 1,
    "priority": 10
})

notify = useNotify()
notify.add(chanify)

notify.publish(
    title="部署完成",
    content="应用版本 v2.1.0 已成功部署到生产环境"
)
```

## 自定义通知渠道

您可以通过继承基础渠道类来创建自定义通知渠道：

```python
from use_notify.channels.base import BaseChannel
import requests

class CustomWebhookChannel(BaseChannel):
    def __init__(self, config):
        super().__init__(config)
        self.webhook_url = config['webhook_url']
        self.headers = config.get('headers', {})
    
    def send(self, title, content, **kwargs):
        """同步发送通知"""
        payload = {
            'title': title,
            'content': content,
            'timestamp': kwargs.get('timestamp'),
            **kwargs
        }
        
        try:
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers=self.headers,
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            print(f"发送失败: {e}")
            return False
    
    async def send_async(self, title, content, **kwargs):
        """异步发送通知"""
        import aiohttp
        
        payload = {
            'title': title,
            'content': content,
            'timestamp': kwargs.get('timestamp'),
            **kwargs
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.webhook_url,
                    json=payload,
                    headers=self.headers,
                    timeout=10
                ) as response:
                    return response.status == 200
        except Exception as e:
            print(f"异步发送失败: {e}")
            return False

# 使用自定义渠道
custom_channel = CustomWebhookChannel({
    'webhook_url': 'https://api.example.com/webhook',
    'headers': {
        'Authorization': 'Bearer your_token',
        'Content-Type': 'application/json'
    }
})

notify = useNotify()
notify.add(custom_channel)
notify.publish("自定义通知", "这是通过自定义渠道发送的消息")
```

## 渠道选择建议

### 移动端推送
- **iOS**: Bark (原生支持，功能丰富)
- **Android**: Pushdeer (开源，支持自建服务器)
- **跨平台**: Pushover (商业服务，稳定可靠)

### 团队协作
- **国内团队**: 钉钉、企业微信 (集成度高，使用广泛)
- **国际团队**: Email (通用性强，支持富文本)

### 开发调试
- **本地开发**: 控制台输出 (Console Channel)
- **测试环境**: Email (便于记录和追踪)
- **生产环境**: 多渠道组合 (确保可靠性)

### 性能考虑
- **高频通知**: 使用异步方法 (`send_async`)
- **批量通知**: 考虑使用队列和批处理
- **关键通知**: 配置多个渠道作为备份

通过合理选择和配置通知渠道，您可以构建一个高效、可靠的通知系统，满足不同场景的需求。
