# 配置管理

use-notify 提供了灵活的配置管理方式，支持环境变量、配置文件、代码配置等多种方式。本指南将详细介绍如何管理和组织通知配置。

## 配置方式

### 1. 代码直接配置

最简单的配置方式是直接在代码中设置：

```python
from use_notify import useNotify, useNotifyChannel

notify = useNotify()
notify.add(useNotifyChannel.Bark({
    "token": "your_bark_token",
    "sound": "default"
}))
```

### 2. 环境变量配置

推荐使用环境变量管理敏感信息：

```python
import os
from use_notify import useNotify, useNotifyChannel

notify = useNotify()
notify.add(useNotifyChannel.Bark({
    "token": os.getenv("BARK_TOKEN"),
    "server": os.getenv("BARK_SERVER", "https://api.day.app"),
    "sound": os.getenv("BARK_SOUND", "default")
}))
```

**环境变量示例：**
```bash
# .env 文件
BARK_TOKEN=your_bark_token
BARK_SERVER=https://api.day.app
BARK_SOUND=default

DING_TOKEN=your_ding_token
DING_SECRET=your_ding_secret

EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_USERNAME=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
EMAIL_RECIPIENTS=recipient1@example.com,recipient2@example.com
```

### 3. 配置文件管理

#### JSON 配置文件

```python
import json
from use_notify import useNotify, useNotifyChannel

def load_notify_from_json(config_file):
    """从 JSON 配置文件加载通知配置"""
    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    notify = useNotify()
    
    for channel_config in config.get('channels', []):
        channel_type = channel_config['type']
        params = channel_config['params']
        
        if channel_type == 'bark':
            notify.add(useNotifyChannel.Bark(params))
        elif channel_type == 'ding':
            notify.add(useNotifyChannel.Ding(params))
        elif channel_type == 'wechat':
            notify.add(useNotifyChannel.WeChat(params))
        elif channel_type == 'email':
            notify.add(useNotifyChannel.Email(params))
        elif channel_type == 'pushover':
            notify.add(useNotifyChannel.Pushover(params))
        elif channel_type == 'pushdeer':
            notify.add(useNotifyChannel.Pushdeer(params))
        elif channel_type == 'chanify':
            notify.add(useNotifyChannel.Chanify(params))
    
    return notify

# 使用配置文件
notify = load_notify_from_json('notify_config.json')
```

**配置文件示例 (`notify_config.json`)：**
```json
{
  "channels": [
    {
      "type": "bark",
      "params": {
        "token": "${BARK_TOKEN}",
        "server": "https://api.day.app",
        "sound": "default",
        "group": "myapp"
      }
    },
    {
      "type": "ding",
      "params": {
        "token": "${DING_TOKEN}",
        "secret": "${DING_SECRET}",
        "at_all": false
      }
    },
    {
      "type": "email",
      "params": {
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
        "username": "${EMAIL_USERNAME}",
        "password": "${EMAIL_PASSWORD}",
        "to_emails": ["${EMAIL_RECIPIENT}"]
      }
    }
  ]
}
```

#### YAML 配置文件

```python
import yaml
from use_notify import useNotify, useNotifyChannel

def load_notify_from_yaml(config_file):
    """从 YAML 配置文件加载通知配置"""
    with open(config_file, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    notify = useNotify()
    
    # 渠道映射
    channel_map = {
        'bark': useNotifyChannel.Bark,
        'ding': useNotifyChannel.Ding,
        'wechat': useNotifyChannel.WeChat,
        'email': useNotifyChannel.Email,
        'pushover': useNotifyChannel.Pushover,
        'pushdeer': useNotifyChannel.Pushdeer,
        'chanify': useNotifyChannel.Chanify
    }
    
    for channel_config in config.get('channels', []):
        channel_type = channel_config['type']
        params = channel_config['params']
        
        if channel_type in channel_map:
            notify.add(channel_map[channel_type](params))
    
    return notify

# 使用 YAML 配置
notify = load_notify_from_yaml('notify_config.yaml')
```

**YAML 配置文件示例 (`notify_config.yaml`)：**
```yaml
channels:
  - type: bark
    params:
      token: ${BARK_TOKEN}
      server: https://api.day.app
      sound: default
      group: myapp
  
  - type: ding
    params:
      token: ${DING_TOKEN}
      secret: ${DING_SECRET}
      at_all: false
  
  - type: email
    params:
      smtp_server: smtp.gmail.com
      smtp_port: 587
      username: ${EMAIL_USERNAME}
      password: ${EMAIL_PASSWORD}
      to_emails:
        - ${EMAIL_RECIPIENT}
```

## 配置模板和变量替换

### 环境变量替换

```python
import os
import re
import json

def replace_env_vars(config_str):
    """替换配置中的环境变量"""
    def replace_var(match):
        var_name = match.group(1)
        default_value = match.group(2) if match.group(2) else ''
        return os.getenv(var_name, default_value)
    
    # 支持 ${VAR} 和 ${VAR:default} 格式
    pattern = r'\$\{([^}:]+)(?::([^}]*))?\}'
    return re.sub(pattern, replace_var, config_str)

def load_config_with_env_vars(config_file):
    """加载配置文件并替换环境变量"""
    with open(config_file, 'r', encoding='utf-8') as f:
        config_str = f.read()
    
    # 替换环境变量
    config_str = replace_env_vars(config_str)
    
    # 解析 JSON
    config = json.loads(config_str)
    return config

# 使用示例
config = load_config_with_env_vars('notify_config.json')
```

### 配置模板

创建可重用的配置模板：

```python
from use_notify import useNotify, useNotifyChannel

class NotifyConfigTemplate:
    """通知配置模板"""
    
    @staticmethod
    def development():
        """开发环境配置"""
        notify = useNotify()
        notify.add(useNotifyChannel.Bark({
            "token": os.getenv("DEV_BARK_TOKEN"),
            "sound": "silence"  # 开发环境使用静音
        }))
        return notify
    
    @staticmethod
    def production():
        """生产环境配置"""
        notify = useNotify()
        notify.add(
            useNotifyChannel.Bark({
                "token": os.getenv("PROD_BARK_TOKEN"),
                "sound": "default"
            }),
            useNotifyChannel.Ding({
                "token": os.getenv("PROD_DING_TOKEN"),
                "secret": os.getenv("PROD_DING_SECRET"),
                "at_all": True
            }),
            useNotifyChannel.Email({
                "smtp_server": "smtp.company.com",
                "smtp_port": 587,
                "username": os.getenv("PROD_EMAIL_USERNAME"),
                "password": os.getenv("PROD_EMAIL_PASSWORD"),
                "to_emails": os.getenv("PROD_EMAIL_RECIPIENTS", "").split(",")
            })
        )
        return notify
    
    @staticmethod
    def testing():
        """测试环境配置"""
        notify = useNotify()
        # 测试环境可以使用控制台输出
        from use_notify.channels import ConsoleChannel
        notify.add(ConsoleChannel())
        return notify

# 根据环境选择配置
env = os.getenv('ENVIRONMENT', 'development')

if env == 'production':
    notify = NotifyConfigTemplate.production()
elif env == 'testing':
    notify = NotifyConfigTemplate.testing()
else:
    notify = NotifyConfigTemplate.development()
```

## 多环境配置管理

### 配置工厂模式

```python
import os
from abc import ABC, abstractmethod
from use_notify import useNotify, useNotifyChannel

class NotifyConfigFactory(ABC):
    """通知配置工厂基类"""
    
    @abstractmethod
    def create_notify(self) -> useNotify:
        pass

class DevelopmentConfig(NotifyConfigFactory):
    """开发环境配置"""
    
    def create_notify(self) -> useNotify:
        notify = useNotify()
        
        # 开发环境只使用轻量级通知
        if os.getenv("DEV_BARK_TOKEN"):
            notify.add(useNotifyChannel.Bark({
                "token": os.getenv("DEV_BARK_TOKEN"),
                "sound": "silence"
            }))
        
        return notify

class ProductionConfig(NotifyConfigFactory):
    """生产环境配置"""
    
    def create_notify(self) -> useNotify:
        notify = useNotify()
        
        # 生产环境使用多渠道确保可靠性
        channels = []
        
        # Bark 通知
        if os.getenv("PROD_BARK_TOKEN"):
            channels.append(useNotifyChannel.Bark({
                "token": os.getenv("PROD_BARK_TOKEN"),
                "sound": "default"
            }))
        
        # 钉钉通知
        if os.getenv("PROD_DING_TOKEN"):
            channels.append(useNotifyChannel.Ding({
                "token": os.getenv("PROD_DING_TOKEN"),
                "secret": os.getenv("PROD_DING_SECRET"),
                "at_all": False
            }))
        
        # 邮件通知
        if all([os.getenv("PROD_EMAIL_USERNAME"), os.getenv("PROD_EMAIL_PASSWORD")]):
            channels.append(useNotifyChannel.Email({
                "smtp_server": os.getenv("PROD_SMTP_SERVER", "smtp.gmail.com"),
                "smtp_port": int(os.getenv("PROD_SMTP_PORT", "587")),
                "username": os.getenv("PROD_EMAIL_USERNAME"),
                "password": os.getenv("PROD_EMAIL_PASSWORD"),
                "to_emails": os.getenv("PROD_EMAIL_RECIPIENTS", "").split(",")
            }))
        
        if channels:
            notify.add(*channels)
        
        return notify

class TestingConfig(NotifyConfigFactory):
    """测试环境配置"""
    
    def create_notify(self) -> useNotify:
        notify = useNotify()
        
        # 测试环境使用模拟通知
        class MockChannel:
            def send(self, title, content, **kwargs):
                print(f"[MOCK] {title}: {content}")
                return True
            
            async def send_async(self, title, content, **kwargs):
                print(f"[MOCK ASYNC] {title}: {content}")
                return True
        
        notify.add(MockChannel())
        return notify

def get_notify_config() -> useNotify:
    """根据环境获取通知配置"""
    env = os.getenv('ENVIRONMENT', 'development').lower()
    
    config_map = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'testing': TestingConfig
    }
    
    config_class = config_map.get(env, DevelopmentConfig)
    return config_class().create_notify()

# 使用配置工厂
notify = get_notify_config()
```

### 配置验证

```python
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class ChannelConfig:
    """通道配置数据类"""
    type: str
    params: Dict
    enabled: bool = True

@dataclass
class NotifyConfig:
    """通知配置数据类"""
    channels: List[ChannelConfig]
    default_title: Optional[str] = None
    timeout: int = 30

class ConfigValidator:
    """配置验证器"""
    
    REQUIRED_PARAMS = {
        'bark': ['token'],
        'ding': ['token'],
        'wechat': ['webhook_url'],
        'email': ['smtp_server', 'smtp_port', 'username', 'password', 'to_emails'],
        'pushover': ['token', 'user'],
        'pushdeer': ['token'],
        'chanify': ['token']
    }
    
    @classmethod
    def validate_channel_config(cls, channel_config: ChannelConfig) -> List[str]:
        """验证单个通道配置"""
        errors = []
        
        # 检查通道类型
        if channel_config.type not in cls.REQUIRED_PARAMS:
            errors.append(f"不支持的通道类型: {channel_config.type}")
            return errors
        
        # 检查必需参数
        required_params = cls.REQUIRED_PARAMS[channel_config.type]
        for param in required_params:
            if param not in channel_config.params or not channel_config.params[param]:
                errors.append(f"{channel_config.type} 通道缺少必需参数: {param}")
        
        # 特定验证
        if channel_config.type == 'email':
            # 验证邮箱格式
            import re
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            
            username = channel_config.params.get('username')
            if username and not re.match(email_pattern, username):
                errors.append(f"邮箱用户名格式不正确: {username}")
            
            to_emails = channel_config.params.get('to_emails', [])
            for email in to_emails:
                if not re.match(email_pattern, email):
                    errors.append(f"收件人邮箱格式不正确: {email}")
        
        return errors
    
    @classmethod
    def validate_config(cls, config: NotifyConfig) -> List[str]:
        """验证完整配置"""
        errors = []
        
        if not config.channels:
            errors.append("至少需要配置一个通知渠道")
            return errors
        
        enabled_channels = [ch for ch in config.channels if ch.enabled]
        if not enabled_channels:
            errors.append("至少需要启用一个通知渠道")
        
        for channel_config in config.channels:
            channel_errors = cls.validate_channel_config(channel_config)
            errors.extend(channel_errors)
        
        return errors

def load_and_validate_config(config_file: str) -> useNotify:
    """加载并验证配置文件"""
    import json
    
    # 加载配置
    with open(config_file, 'r', encoding='utf-8') as f:
        raw_config = json.load(f)
    
    # 转换为数据类
    channels = [
        ChannelConfig(
            type=ch['type'],
            params=ch['params'],
            enabled=ch.get('enabled', True)
        )
        for ch in raw_config.get('channels', [])
    ]
    
    config = NotifyConfig(
        channels=channels,
        default_title=raw_config.get('default_title'),
        timeout=raw_config.get('timeout', 30)
    )
    
    # 验证配置
    errors = ConfigValidator.validate_config(config)
    if errors:
        raise ValueError(f"配置验证失败:\n" + "\n".join(f"- {error}" for error in errors))
    
    # 创建通知实例
    notify = useNotify()
    
    channel_map = {
        'bark': useNotifyChannel.Bark,
        'ding': useNotifyChannel.Ding,
        'wechat': useNotifyChannel.WeChat,
        'email': useNotifyChannel.Email,
        'pushover': useNotifyChannel.Pushover,
        'pushdeer': useNotifyChannel.Pushdeer,
        'chanify': useNotifyChannel.Chanify
    }
    
    for channel_config in config.channels:
        if channel_config.enabled and channel_config.type in channel_map:
            notify.add(channel_map[channel_config.type](channel_config.params))
    
    return notify

# 使用验证配置
try:
    notify = load_and_validate_config('notify_config.json')
    print("配置加载成功")
except ValueError as e:
    print(f"配置错误: {e}")
```

## 配置最佳实践

### 1. 安全性

```python
# ✅ 推荐：使用环境变量存储敏感信息
notify.add(useNotifyChannel.Email({
    "username": os.getenv("EMAIL_USERNAME"),
    "password": os.getenv("EMAIL_PASSWORD")
}))

# ❌ 不推荐：在代码中硬编码敏感信息
notify.add(useNotifyChannel.Email({
    "username": "user@example.com",
    "password": "hardcoded_password"  # 安全风险
}))
```

### 2. 可维护性

```python
# ✅ 推荐：使用配置文件集中管理
notify = load_notify_from_json('config/notify.json')

# ✅ 推荐：使用工厂模式支持多环境
notify = get_notify_config()

# ❌ 不推荐：在多处重复配置
# 在多个文件中重复相同的配置代码
```

### 3. 灵活性

```python
# ✅ 推荐：支持动态配置
class DynamicNotifyConfig:
    def __init__(self):
        self.notify = useNotify()
        self.load_config()
    
    def load_config(self):
        """动态加载配置"""
        config_file = os.getenv('NOTIFY_CONFIG_FILE', 'notify_config.json')
        if os.path.exists(config_file):
            # 重新加载配置
            self.notify = load_notify_from_json(config_file)
    
    def reload_config(self):
        """重新加载配置"""
        self.load_config()

# 支持配置热重载
dynamic_notify = DynamicNotifyConfig()
```

### 4. 测试友好

```python
# ✅ 推荐：提供测试配置
class TestNotifyConfig:
    @staticmethod
    def create_test_notify():
        """创建测试用通知实例"""
        notify = useNotify()
        
        # 使用模拟通道进行测试
        class TestChannel:
            def __init__(self):
                self.sent_messages = []
            
            def send(self, title, content, **kwargs):
                self.sent_messages.append({
                    'title': title,
                    'content': content,
                    'kwargs': kwargs
                })
                return True
            
            async def send_async(self, title, content, **kwargs):
                return self.send(title, content, **kwargs)
        
        test_channel = TestChannel()
        notify.add(test_channel)
        
        # 添加验证方法
        notify._test_channel = test_channel
        return notify

# 在测试中使用
def test_notification():
    notify = TestNotifyConfig.create_test_notify()
    notify.publish(title="测试", content="测试消息")
    
    # 验证消息是否发送
    assert len(notify._test_channel.sent_messages) == 1
    assert notify._test_channel.sent_messages[0]['title'] == "测试"
```

通过合理的配置管理，可以让 use-notify 在不同环境下灵活运行，同时保证安全性和可维护性。选择适合项目需求的配置方式，并遵循最佳实践，能够大大提升开发效率和系统稳定性。