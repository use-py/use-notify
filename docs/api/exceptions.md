# 异常类 API

use-notify 定义了一系列自定义异常类，用于处理通知系统中的各种错误情况。这些异常类提供了清晰的错误分类和详细的错误信息。

## 导入

```python
from use_notify.exceptions import (
    NotifyConfigError,
    NotifySendError,
    NotifyTimeoutError,
    NotifyChannelError
)

# 或者导入所有异常
from use_notify.exceptions import *
```

## 异常层次结构

```
Exception
├── NotifyError (基础异常类)
    ├── NotifyConfigError (配置错误)
    ├── NotifySendError (发送错误)
    ├── NotifyTimeoutError (超时错误)
    └── NotifyChannelError (渠道错误)
```

## 基础异常类

### `NotifyError`

所有 use-notify 异常的基类。

```python
class NotifyError(Exception):
    """use-notify 基础异常类"""
    
    def __init__(self, message: str, details: dict = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}
    
    def __str__(self):
        if self.details:
            return f"{self.message} (详情: {self.details})"
        return self.message
```

**属性：**
- `message` (str): 错误消息
- `details` (dict): 错误详情字典

**使用场景：**
- 作为其他异常的基类
- 捕获所有 use-notify 相关异常

```python
try:
    # use-notify 相关操作
    notify.publish("标题", "内容")
except NotifyError as e:
    print(f"通知系统错误: {e}")
    if e.details:
        print(f"错误详情: {e.details}")
```

## 配置异常

### `NotifyConfigError`

通知渠道配置错误时抛出的异常。

```python
class NotifyConfigError(NotifyError):
    """通知配置错误"""
    
    def __init__(self, message: str, channel_type: str = None, config: dict = None):
        details = {}
        if channel_type:
            details['channel_type'] = channel_type
        if config:
            details['config'] = config
        super().__init__(message, details)
        self.channel_type = channel_type
        self.config = config
```

**属性：**
- `channel_type` (str): 出错的渠道类型
- `config` (dict): 导致错误的配置

**常见触发场景：**
1. 缺少必需的配置参数
2. 配置参数类型错误
3. 配置参数值无效
4. 渠道类型不支持

#### 使用示例

```python
from use_notify import useNotify, useNotifyChannel
from use_notify.exceptions import NotifyConfigError

try:
    # 缺少必需参数
    bark = useNotifyChannel.Bark({})  # 缺少 token
except NotifyConfigError as e:
    print(f"配置错误: {e.message}")
    print(f"渠道类型: {e.channel_type}")
    print(f"错误配置: {e.config}")

try:
    # 参数类型错误
    email = useNotifyChannel.Email({
        "smtp_server": "smtp.gmail.com",
        "smtp_port": "587",  # 应该是 int 类型
        "username": "user@gmail.com",
        "password": "password",
        "to_emails": "user@example.com"  # 应该是 list 类型
    })
except NotifyConfigError as e:
    print(f"类型错误: {e}")

try:
    # 无效的配置值
    ding = useNotifyChannel.Ding({
        "token": "",  # 空 token
        "msg_type": "invalid_type"  # 无效的消息类型
    })
except NotifyConfigError as e:
    print(f"值错误: {e}")
```

#### 配置验证示例

```python
def validate_bark_config(config):
    """验证 Bark 配置"""
    required_fields = ['token']
    
    for field in required_fields:
        if field not in config:
            raise NotifyConfigError(
                f"Bark 配置缺少必需字段: {field}",
                channel_type="Bark",
                config=config
            )
    
    if not isinstance(config['token'], str) or not config['token'].strip():
        raise NotifyConfigError(
            "Bark token 必须是非空字符串",
            channel_type="Bark",
            config=config
        )
    
    if 'server' in config and not config['server'].startswith(('http://', 'https://')):
        raise NotifyConfigError(
            "Bark server 必须是有效的 HTTP/HTTPS URL",
            channel_type="Bark",
            config=config
        )

# 使用配置验证
try:
    config = {"token": ""}
    validate_bark_config(config)
except NotifyConfigError as e:
    print(f"配置验证失败: {e}")
```

## 发送异常

### `NotifySendError`

通知发送失败时抛出的异常。

```python
class NotifySendError(NotifyError):
    """通知发送错误"""
    
    def __init__(self, message: str, channel_type: str = None, 
                 status_code: int = None, response_text: str = None):
        details = {}
        if channel_type:
            details['channel_type'] = channel_type
        if status_code:
            details['status_code'] = status_code
        if response_text:
            details['response_text'] = response_text
        super().__init__(message, details)
        self.channel_type = channel_type
        self.status_code = status_code
        self.response_text = response_text
```

**属性：**
- `channel_type` (str): 发送失败的渠道类型
- `status_code` (int): HTTP 状态码（如果适用）
- `response_text` (str): 服务器响应文本

**常见触发场景：**
1. 网络连接失败
2. 认证失败（token 无效）
3. 服务器错误（5xx 状态码）
4. 请求格式错误（4xx 状态码）
5. 服务限流或配额超限

#### 使用示例

```python
from use_notify import useNotify, useNotifyChannel
from use_notify.exceptions import NotifySendError

notify = useNotify()
notify.add(useNotifyChannel.Bark({"token": "invalid_token"}))

try:
    result = notify.publish("测试", "测试内容")
except NotifySendError as e:
    print(f"发送失败: {e.message}")
    print(f"渠道: {e.channel_type}")
    print(f"状态码: {e.status_code}")
    print(f"响应: {e.response_text}")
    
    # 根据错误类型进行不同处理
    if e.status_code == 401:
        print("认证失败，请检查 token")
    elif e.status_code == 429:
        print("请求过于频繁，请稍后重试")
    elif e.status_code >= 500:
        print("服务器错误，请稍后重试")
    else:
        print("其他错误，请检查配置")
```

#### 重试机制示例

```python
import time
from use_notify.exceptions import NotifySendError

def send_with_retry(notify, title, content, max_retries=3, delay=1):
    """带重试的发送通知"""
    last_exception = None
    
    for attempt in range(max_retries + 1):
        try:
            return notify.publish(title, content)
        except NotifySendError as e:
            last_exception = e
            
            # 某些错误不值得重试
            if e.status_code in [400, 401, 403, 404]:
                print(f"客户端错误 {e.status_code}，不重试")
                raise
            
            if attempt < max_retries:
                wait_time = delay * (2 ** attempt)  # 指数退避
                print(f"发送失败 (尝试 {attempt + 1}/{max_retries + 1})，{wait_time}秒后重试")
                print(f"错误: {e}")
                time.sleep(wait_time)
            else:
                print(f"所有重试都失败了")
    
    raise last_exception

# 使用重试机制
notify = useNotify()
notify.add(useNotifyChannel.Bark({"token": "your_token"}))

try:
    send_with_retry(notify, "重要通知", "这是一条重要消息")
except NotifySendError as e:
    print(f"最终发送失败: {e}")
```

## 超时异常

### `NotifyTimeoutError`

通知发送超时时抛出的异常。

```python
class NotifyTimeoutError(NotifyError):
    """通知发送超时错误"""
    
    def __init__(self, message: str, timeout: float = None, channel_type: str = None):
        details = {}
        if timeout:
            details['timeout'] = timeout
        if channel_type:
            details['channel_type'] = channel_type
        super().__init__(message, details)
        self.timeout = timeout
        self.channel_type = channel_type
```

**属性：**
- `timeout` (float): 超时时间（秒）
- `channel_type` (str): 超时的渠道类型

**常见触发场景：**
1. 网络延迟过高
2. 服务器响应缓慢
3. 设置的超时时间过短

#### 使用示例

```python
import asyncio
from use_notify import useNotify, useNotifyChannel
from use_notify.exceptions import NotifyTimeoutError

async def send_with_timeout(notify, title, content, timeout=5.0):
    """带超时的异步发送"""
    try:
        result = await asyncio.wait_for(
            notify.publish_async(title, content),
            timeout=timeout
        )
        return result
    except asyncio.TimeoutError:
        raise NotifyTimeoutError(
            f"通知发送超时 ({timeout}秒)",
            timeout=timeout
        )

# 使用超时发送
async def main():
    notify = useNotify()
    notify.add(useNotifyChannel.Bark({"token": "your_token"}))
    
    try:
        await send_with_timeout(notify, "测试", "测试内容", timeout=3.0)
        print("发送成功")
    except NotifyTimeoutError as e:
        print(f"发送超时: {e}")
        print(f"超时时间: {e.timeout}秒")
        
        # 可以尝试更长的超时时间
        try:
            await send_with_timeout(notify, "测试", "测试内容", timeout=10.0)
            print("延长超时后发送成功")
        except NotifyTimeoutError:
            print("即使延长超时时间也发送失败")

asyncio.run(main())
```

## 渠道异常

### `NotifyChannelError`

通知渠道相关错误时抛出的异常。

```python
class NotifyChannelError(NotifyError):
    """通知渠道错误"""
    
    def __init__(self, message: str, channel_type: str = None, operation: str = None):
        details = {}
        if channel_type:
            details['channel_type'] = channel_type
        if operation:
            details['operation'] = operation
        super().__init__(message, details)
        self.channel_type = channel_type
        self.operation = operation
```

**属性：**
- `channel_type` (str): 出错的渠道类型
- `operation` (str): 出错的操作类型

**常见触发场景：**
1. 渠道初始化失败
2. 渠道不支持某种操作
3. 渠道状态异常

#### 使用示例

```python
from use_notify.exceptions import NotifyChannelError

class CustomChannel:
    """自定义渠道示例"""
    
    def __init__(self, config):
        self.config = config
        self.initialized = False
    
    def initialize(self):
        """初始化渠道"""
        try:
            # 模拟初始化过程
            if not self.config.get('api_key'):
                raise NotifyChannelError(
                    "渠道初始化失败：缺少 API 密钥",
                    channel_type="CustomChannel",
                    operation="initialize"
                )
            self.initialized = True
        except Exception as e:
            raise NotifyChannelError(
                f"渠道初始化异常: {e}",
                channel_type="CustomChannel",
                operation="initialize"
            )
    
    def send(self, title, content):
        """发送通知"""
        if not self.initialized:
            raise NotifyChannelError(
                "渠道未初始化",
                channel_type="CustomChannel",
                operation="send"
            )
        
        # 模拟发送逻辑
        print(f"发送通知: {title} - {content}")

# 使用自定义渠道
try:
    channel = CustomChannel({})  # 缺少 api_key
    channel.initialize()
except NotifyChannelError as e:
    print(f"渠道错误: {e}")
    print(f"渠道类型: {e.channel_type}")
    print(f"操作: {e.operation}")
```

## 异常处理最佳实践

### 1. 分层异常处理

```python
from use_notify import useNotify, useNotifyChannel
from use_notify.exceptions import (
    NotifyError, NotifyConfigError, NotifySendError, 
    NotifyTimeoutError, NotifyChannelError
)

def robust_notification_system():
    """健壮的通知系统"""
    try:
        # 配置通知
        notify = useNotify()
        
        try:
            notify.add(useNotifyChannel.Bark({"token": "your_token"}))
        except NotifyConfigError as e:
            print(f"配置错误，使用备用渠道: {e}")
            # 使用备用配置
            notify.add(useNotifyChannel.Email({
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "username": "backup@example.com",
                "password": "backup_password",
                "to_emails": ["admin@example.com"]
            }))
        
        # 发送通知
        try:
            result = notify.publish("系统通知", "这是一条重要消息")
            return result
        except NotifyTimeoutError as e:
            print(f"发送超时，记录到日志: {e}")
            log_notification_failure("timeout", str(e))
            return False
        except NotifySendError as e:
            print(f"发送失败，尝试备用方案: {e}")
            return try_fallback_notification("系统通知", "这是一条重要消息")
        except NotifyChannelError as e:
            print(f"渠道错误，禁用该渠道: {e}")
            disable_problematic_channel(e.channel_type)
            return False
            
    except NotifyError as e:
        # 捕获所有其他通知相关错误
        print(f"通知系统错误: {e}")
        log_notification_failure("general", str(e))
        return False
    except Exception as e:
        # 捕获意外错误
        print(f"意外错误: {e}")
        log_notification_failure("unexpected", str(e))
        return False

def log_notification_failure(error_type, message):
    """记录通知失败日志"""
    import logging
    logging.error(f"通知失败 [{error_type}]: {message}")

def try_fallback_notification(title, content):
    """尝试备用通知方案"""
    try:
        # 使用最简单的备用方案（如文件日志）
        with open("notification_fallback.log", "a") as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {title}: {content}\n")
        return True
    except Exception:
        return False

def disable_problematic_channel(channel_type):
    """禁用有问题的渠道"""
    print(f"将渠道 {channel_type} 标记为不可用")
    # 实现渠道禁用逻辑
```

### 2. 异常信息收集

```python
import traceback
from use_notify.exceptions import NotifyError

class NotificationErrorCollector:
    """通知错误收集器"""
    
    def __init__(self):
        self.errors = []
    
    def collect_error(self, error, context=None):
        """收集错误信息"""
        error_info = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'error_type': type(error).__name__,
            'message': str(error),
            'traceback': traceback.format_exc(),
            'context': context or {}
        }
        
        if isinstance(error, NotifyError):
            error_info['details'] = error.details
            if hasattr(error, 'channel_type'):
                error_info['channel_type'] = error.channel_type
            if hasattr(error, 'status_code'):
                error_info['status_code'] = error.status_code
        
        self.errors.append(error_info)
    
    def get_error_summary(self):
        """获取错误摘要"""
        if not self.errors:
            return "无错误记录"
        
        summary = {
            'total_errors': len(self.errors),
            'error_types': {},
            'channel_errors': {},
            'recent_errors': self.errors[-5:]  # 最近5个错误
        }
        
        for error in self.errors:
            error_type = error['error_type']
            summary['error_types'][error_type] = summary['error_types'].get(error_type, 0) + 1
            
            if 'channel_type' in error:
                channel = error['channel_type']
                summary['channel_errors'][channel] = summary['channel_errors'].get(channel, 0) + 1
        
        return summary

# 使用错误收集器
error_collector = NotificationErrorCollector()

def send_notification_with_error_tracking(notify, title, content):
    """带错误跟踪的发送通知"""
    try:
        return notify.publish(title, content)
    except NotifyError as e:
        error_collector.collect_error(e, {
            'title': title,
            'content_length': len(content),
            'channel_count': len(notify.channels)
        })
        raise
    except Exception as e:
        error_collector.collect_error(e, {
            'title': title,
            'content_length': len(content)
        })
        raise

# 定期检查错误摘要
def check_error_summary():
    summary = error_collector.get_error_summary()
    if summary['total_errors'] > 0:
        print(f"错误摘要: {summary}")
        
        # 如果某个渠道错误过多，可以考虑禁用
        for channel, count in summary['channel_errors'].items():
            if count > 10:  # 阈值
                print(f"警告: 渠道 {channel} 错误次数过多 ({count})")
```

### 3. 自定义异常处理器

```python
from use_notify.exceptions import NotifyError

class NotificationErrorHandler:
    """通知错误处理器"""
    
    def __init__(self):
        self.handlers = {}
    
    def register_handler(self, exception_type, handler_func):
        """注册异常处理器"""
        self.handlers[exception_type] = handler_func
    
    def handle_error(self, error):
        """处理错误"""
        error_type = type(error)
        
        # 查找最匹配的处理器
        for exc_type, handler in self.handlers.items():
            if isinstance(error, exc_type):
                return handler(error)
        
        # 默认处理器
        return self.default_handler(error)
    
    def default_handler(self, error):
        """默认错误处理器"""
        print(f"未处理的错误: {error}")
        return False

# 创建错误处理器
error_handler = NotificationErrorHandler()

# 注册具体的处理器
def handle_config_error(error):
    print(f"配置错误: {error.message}")
    if error.channel_type:
        print(f"问题渠道: {error.channel_type}")
    # 可以尝试使用默认配置
    return "use_default_config"

def handle_send_error(error):
    print(f"发送错误: {error.message}")
    if error.status_code == 429:
        print("触发限流，等待后重试")
        return "retry_later"
    elif error.status_code >= 500:
        print("服务器错误，稍后重试")
        return "retry_later"
    else:
        print("客户端错误，检查配置")
        return "check_config"

def handle_timeout_error(error):
    print(f"超时错误: {error.message}")
    print(f"超时时间: {error.timeout}秒")
    return "increase_timeout"

# 注册处理器
error_handler.register_handler(NotifyConfigError, handle_config_error)
error_handler.register_handler(NotifySendError, handle_send_error)
error_handler.register_handler(NotifyTimeoutError, handle_timeout_error)

# 使用错误处理器
def robust_send_notification(notify, title, content):
    """健壮的发送通知"""
    try:
        return notify.publish(title, content)
    except NotifyError as e:
        action = error_handler.handle_error(e)
        
        if action == "retry_later":
            # 实现重试逻辑
            time.sleep(5)
            return robust_send_notification(notify, title, content)
        elif action == "use_default_config":
            # 使用默认配置重试
            return try_with_default_config(title, content)
        elif action == "increase_timeout":
            # 增加超时时间重试
            return try_with_longer_timeout(notify, title, content)
        else:
            return False
```

通过合理使用这些异常类和处理策略，您可以构建一个健壮、可靠的通知系统，能够优雅地处理各种错误情况并提供有用的错误信息。