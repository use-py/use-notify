# useNotify 类

`useNotify` 是 use-notify 的核心类，负责管理通知渠道和发送通知。它提供了简洁的 API 来添加多个通知渠道并统一发送消息。

## 类定义

```python
class useNotify:
    """通知管理器"""
    
    def __init__(self):
        """初始化通知管理器"""
        pass
```

## 构造函数

### `__init__()`

创建一个新的通知管理器实例。

```python
from use_notify import useNotify

notify = useNotify()
```

**参数：**
- 无参数

**返回值：**
- `useNotify` 实例

## 实例方法

### `add(*channels)`

添加一个或多个通知渠道到管理器中。

```python
from use_notify import useNotify, useNotifyChannel

notify = useNotify()

# 添加单个渠道
notify.add(useNotifyChannel.Bark({"token": "your_token"}))

# 添加多个渠道
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
```

**参数：**
- `*channels` (可变参数): 一个或多个通知渠道实例

**返回值：**
- `None`

**异常：**
- `NotifyConfigError`: 当传入的渠道配置无效时抛出

**示例：**
```python
# 错误示例 - 会抛出 NotifyConfigError
try:
    notify.add("invalid_channel")
except NotifyConfigError as e:
    print(f"配置错误: {e}")
```

### `publish(title, content, **kwargs)`

同步发送通知到所有已添加的渠道。

```python
notify = useNotify()
notify.add(useNotifyChannel.Bark({"token": "your_token"}))

# 基本用法
notify.publish(title="通知标题", content="通知内容")

# 带额外参数
notify.publish(
    title="系统警报",
    content="CPU使用率过高",
    priority="high",
    tags=["system", "alert"]
)
```

**参数：**
- `title` (str): 通知标题
- `content` (str): 通知内容
- `**kwargs`: 额外的参数，会传递给各个通知渠道

**返回值：**
- `bool`: 如果至少有一个渠道发送成功则返回 `True`，否则返回 `False`

**异常：**
- `NotifySendError`: 当所有渠道都发送失败时抛出

**行为说明：**
- 会并发向所有渠道发送通知
- 如果某个渠道发送失败，不会影响其他渠道
- 只有当所有渠道都失败时才会抛出异常

### `publish_async(title, content, **kwargs)`

异步发送通知到所有已添加的渠道。

```python
import asyncio
from use_notify import useNotify, useNotifyChannel

async def send_notification():
    notify = useNotify()
    notify.add(useNotifyChannel.Bark({"token": "your_token"}))
    
    # 异步发送
    result = await notify.publish_async(
        title="异步通知",
        content="这是一条异步发送的通知"
    )
    
    print(f"发送结果: {result}")

# 运行异步函数
asyncio.run(send_notification())
```

**参数：**
- `title` (str): 通知标题
- `content` (str): 通知内容
- `**kwargs`: 额外的参数，会传递给各个通知渠道

**返回值：**
- `bool`: 如果至少有一个渠道发送成功则返回 `True`，否则返回 `False`

**异常：**
- `NotifySendError`: 当所有渠道都发送失败时抛出

**性能优势：**
- 使用 `asyncio.gather()` 并发发送到所有渠道
- 比同步版本更高效，特别是在有多个渠道时
- 不会阻塞调用线程

### `remove_all()`

移除所有已添加的通知渠道。

```python
notify = useNotify()
notify.add(
    useNotifyChannel.Bark({"token": "bark_token"}),
    useNotifyChannel.Ding({"token": "ding_token"})
)

print(f"渠道数量: {len(notify.channels)}")  # 输出: 2

# 移除所有渠道
notify.remove_all()

print(f"渠道数量: {len(notify.channels)}")  # 输出: 0
```

**参数：**
- 无参数

**返回值：**
- `None`

**用途：**
- 重置通知管理器
- 在测试中清理状态
- 动态重新配置通知渠道

## 属性

### `channels`

只读属性，返回当前已添加的通知渠道列表。

```python
notify = useNotify()
notify.add(
    useNotifyChannel.Bark({"token": "bark_token"}),
    useNotifyChannel.Ding({"token": "ding_token"})
)

print(f"当前渠道数量: {len(notify.channels)}")
for i, channel in enumerate(notify.channels):
    print(f"渠道 {i + 1}: {type(channel).__name__}")
```

**类型：**
- `list`: 通知渠道实例列表

## 使用示例

### 基本使用

```python
from use_notify import useNotify, useNotifyChannel

# 创建通知管理器
notify = useNotify()

# 添加通知渠道
notify.add(
    useNotifyChannel.Bark({"token": "your_bark_token"}),
    useNotifyChannel.Ding({"token": "your_ding_token"})
)

# 发送通知
notify.publish(
    title="任务完成",
    content="数据处理任务已成功完成"
)
```

### 错误处理

```python
from use_notify import useNotify, useNotifyChannel
from use_notify.exceptions import NotifyConfigError, NotifySendError

notify = useNotify()

try:
    # 添加渠道
    notify.add(useNotifyChannel.Bark({"token": "your_token"}))
    
    # 发送通知
    result = notify.publish(title="测试", content="测试内容")
    
    if result:
        print("通知发送成功")
    else:
        print("通知发送失败")
        
except NotifyConfigError as e:
    print(f"配置错误: {e}")
except NotifySendError as e:
    print(f"发送错误: {e}")
except Exception as e:
    print(f"未知错误: {e}")
```

### 异步使用

```python
import asyncio
from use_notify import useNotify, useNotifyChannel

async def async_notification_example():
    notify = useNotify()
    
    # 添加多个渠道
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
    
    # 并发发送多条通知
    tasks = [
        notify.publish_async(title="通知1", content="内容1"),
        notify.publish_async(title="通知2", content="内容2"),
        notify.publish_async(title="通知3", content="内容3")
    ]
    
    results = await asyncio.gather(*tasks)
    
    for i, result in enumerate(results, 1):
        print(f"通知{i} 发送{'成功' if result else '失败'}")

# 运行异步示例
asyncio.run(async_notification_example())
```

### 动态管理渠道

```python
from use_notify import useNotify, useNotifyChannel

class DynamicNotifyManager:
    def __init__(self):
        self.notify = useNotify()
        self.channel_configs = {}
    
    def add_channel(self, name, channel_type, config):
        """动态添加渠道"""
        if channel_type == 'bark':
            channel = useNotifyChannel.Bark(config)
        elif channel_type == 'ding':
            channel = useNotifyChannel.Ding(config)
        elif channel_type == 'email':
            channel = useNotifyChannel.Email(config)
        else:
            raise ValueError(f"不支持的渠道类型: {channel_type}")
        
        self.notify.add(channel)
        self.channel_configs[name] = {'type': channel_type, 'config': config}
    
    def remove_all_channels(self):
        """移除所有渠道"""
        self.notify.remove_all()
        self.channel_configs.clear()
    
    def send_notification(self, title, content):
        """发送通知"""
        if not self.notify.channels:
            print("警告: 没有配置任何通知渠道")
            return False
        
        return self.notify.publish(title=title, content=content)
    
    def get_channel_info(self):
        """获取渠道信息"""
        return {
            'count': len(self.notify.channels),
            'configs': self.channel_configs
        }

# 使用动态管理器
manager = DynamicNotifyManager()

# 添加渠道
manager.add_channel('bark', 'bark', {'token': 'bark_token'})
manager.add_channel('ding', 'ding', {'token': 'ding_token'})

# 发送通知
manager.send_notification('动态通知', '这是通过动态管理器发送的通知')

# 查看渠道信息
info = manager.get_channel_info()
print(f"当前配置了 {info['count']} 个渠道")
```

### 条件发送

```python
from use_notify import useNotify, useNotifyChannel

class ConditionalNotify:
    def __init__(self):
        self.notify = useNotify()
        self.notify.add(useNotifyChannel.Bark({"token": "your_token"}))
    
    def send_if_error(self, title, content, error_level='info'):
        """只在错误级别达到阈值时发送通知"""
        error_levels = {'info': 0, 'warning': 1, 'error': 2, 'critical': 3}
        threshold = error_levels.get('warning', 1)  # 默认阈值
        
        if error_levels.get(error_level, 0) >= threshold:
            return self.notify.publish(title=title, content=content)
        else:
            print(f"错误级别 {error_level} 未达到通知阈值，跳过发送")
            return False
    
    def send_if_condition(self, title, content, condition_func, *args, **kwargs):
        """根据自定义条件发送通知"""
        if condition_func(*args, **kwargs):
            return self.notify.publish(title=title, content=content)
        else:
            print("条件不满足，跳过发送通知")
            return False

# 使用条件发送
conditional_notify = ConditionalNotify()

# 根据错误级别发送
conditional_notify.send_if_error("系统警告", "磁盘空间不足", "warning")  # 会发送
conditional_notify.send_if_error("调试信息", "用户登录", "info")  # 不会发送

# 根据自定义条件发送
def cpu_usage_high(usage):
    return usage > 80

conditional_notify.send_if_condition(
    "CPU警报", 
    "CPU使用率过高", 
    cpu_usage_high, 
    85  # CPU使用率
)  # 会发送
```

## 最佳实践

### 1. 单例模式

```python
class NotifyManager:
    _instance = None
    _notify = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._notify = useNotify()
        return cls._instance
    
    def get_notify(self):
        return self._notify

# 全局使用
notify_manager = NotifyManager()
notify = notify_manager.get_notify()
```

### 2. 配置分离

```python
import os
from use_notify import useNotify, useNotifyChannel

def create_notify_from_env():
    """从环境变量创建通知实例"""
    notify = useNotify()
    
    # Bark 配置
    if os.getenv('BARK_TOKEN'):
        notify.add(useNotifyChannel.Bark({
            'token': os.getenv('BARK_TOKEN'),
            'server': os.getenv('BARK_SERVER', 'https://api.day.app')
        }))
    
    # 钉钉配置
    if os.getenv('DING_TOKEN'):
        notify.add(useNotifyChannel.Ding({
            'token': os.getenv('DING_TOKEN'),
            'secret': os.getenv('DING_SECRET')
        }))
    
    return notify

# 使用环境变量配置
notify = create_notify_from_env()
```

### 3. 错误重试

```python
import time
from use_notify import useNotify, useNotifyChannel
from use_notify.exceptions import NotifySendError

class RetryableNotify:
    def __init__(self, max_retries=3, retry_delay=1):
        self.notify = useNotify()
        self.max_retries = max_retries
        self.retry_delay = retry_delay
    
    def add_channel(self, channel):
        self.notify.add(channel)
    
    def publish_with_retry(self, title, content, **kwargs):
        """带重试的发送通知"""
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return self.notify.publish(title=title, content=content, **kwargs)
            except NotifySendError as e:
                last_exception = e
                if attempt < self.max_retries:
                    print(f"发送失败，{self.retry_delay}秒后重试 (尝试 {attempt + 1}/{self.max_retries + 1})")
                    time.sleep(self.retry_delay)
                    self.retry_delay *= 2  # 指数退避
        
        raise last_exception

# 使用重试通知
retry_notify = RetryableNotify(max_retries=3)
retry_notify.add_channel(useNotifyChannel.Bark({"token": "your_token"}))

try:
    retry_notify.publish_with_retry("重要通知", "这是一条重要消息")
except NotifySendError as e:
    print(f"重试后仍然失败: {e}")
```

通过合理使用 `useNotify` 类的各种方法和特性，您可以构建一个强大而灵活的通知系统，满足各种复杂的业务需求。