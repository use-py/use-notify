# Loguru 日志上报集成

本文档介绍如何使用 use-notify 库集成 loguru 实现日志上报功能。

## 功能特性

- 🚀 **简单易用**: 通过 `logger.report()` 方法即可实现日志上报
- 🔧 **灵活配置**: 支持多种配置方式和自定义日志级别
- 📱 **多渠道支持**: 支持所有 use-notify 的通知渠道
- 🛡️ **异常安全**: 上报失败不会影响主程序运行
- 📊 **丰富信息**: 自动包含时间、级别、模块、函数等详细信息

## 快速开始

### 1. 基础使用

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

### 2. 使用通道实例

```python
from use_notify import useNotifyChannel, setup_loguru_reporter

# 直接使用通道实例
channels = [
    useNotifyChannel.Bark({"token": "your_bark_token"}),
    useNotifyChannel.WeChat({"token": "your_wechat_token"}),
]

# 设置上报器
setup_loguru_reporter(channels=channels, level="WARNING")

# 上报消息
logger.report("这是一条警告消息", level="WARNING")
```

### 3. 手动设置

```python
from use_notify import LoguruReporter, useNotify, useNotifyChannel

# 创建通知实例
notify = useNotify()
notify.add(
    useNotifyChannel.Bark({"token": "your_bark_token"}),
    useNotifyChannel.WeChat({"token": "your_wechat_token"}),
)

# 创建上报器
reporter = LoguruReporter(notify)

# 配置logger
reporter.configure_logger(level="INFO")

# 上报消息
logger.report("手动设置的上报消息", level="INFO", 模块="demo")
```

## API 参考

### setup_loguru_reporter

设置全局loguru上报器的便捷函数。

```python
setup_loguru_reporter(
    settings: Optional[Dict[str, Any]] = None,
    channels: Optional[List] = None,
    level: str = "ERROR"
) -> LoguruReporter
```

**参数:**
- `settings`: 通知渠道配置字典
- `channels`: 通知渠道实例列表
- `level`: 触发上报的最低日志级别

**返回:** LoguruReporter实例

### LoguruReporter

主要的日志上报器类。

#### 方法

##### `__init__(notify_instance: Optional[Notify] = None)`

初始化上报器。

##### `add_channel(*channels)`

添加通知渠道。

##### `configure_logger(level: str = "ERROR", format_string: Optional[str] = None)`

配置loguru logger。

**参数:**
- `level`: 日志级别
- `format_string`: 自定义格式字符串

##### `from_settings(cls, settings: Dict[str, Any], level: str = "ERROR")`

从配置创建LoguruReporter实例。

### logger.report

上报日志消息的方法（在配置后自动添加到logger）。

```python
logger.report(
    message: str, 
    level: str = "ERROR", 
    **extra_info
)
```

**参数:**
- `message`: 要上报的消息
- `level`: 日志级别（INFO, WARNING, ERROR, CRITICAL）
- `**extra_info`: 额外的上报信息

## 支持的日志级别

- `DEBUG`: 调试信息
- `INFO`: 一般信息
- `WARNING`: 警告信息
- `ERROR`: 错误信息
- `CRITICAL`: 严重错误

## 上报消息格式

上报的消息会包含以下信息：

- **时间**: 日志记录时间
- **级别**: 日志级别
- **模块**: 记录日志的模块名
- **函数**: 记录日志的函数名和行号
- **消息**: 日志消息内容
- **异常**: 异常信息（如果有）
- **额外信息**: 通过 `**extra_info` 传入的自定义信息

## 使用场景

### 1. 异常监控

```python
try:
    # 业务代码
    result = risky_operation()
except Exception as e:
    logger.report(
        f"业务操作失败: {str(e)}", 
        level="ERROR",
        操作="risky_operation",
        用户ID="12345"
    )
```

### 2. 关键业务节点监控

```python
# 用户登录成功
logger.report(
    "用户登录成功", 
    level="INFO",
    用户ID=user_id,
    IP地址=request.remote_addr
)

# 支付完成
logger.report(
    "支付完成", 
    level="INFO",
    订单号=order_id,
    金额=amount,
    支付方式=payment_method
)
```

### 3. 系统状态监控

```python
# 内存使用率过高
if memory_usage > 0.9:
    logger.report(
        "内存使用率过高", 
        level="WARNING",
        当前使用率=f"{memory_usage:.2%}",
        服务器=server_name
    )

# 数据库连接失败
logger.report(
    "数据库连接失败", 
    level="CRITICAL",
    数据库=db_name,
    重试次数=retry_count
)
```

## 类型检查支持

为了获得更好的IDE支持和类型检查，建议在使用时添加类型注解：

```python
from loguru import logger
from use_notify import setup_loguru_reporter
from typing import TYPE_CHECKING

# 类型检查时使用扩展的Logger类型
if TYPE_CHECKING:
    from use_notify.loguru_types import ExtendedLogger
    logger = logger  # type: ExtendedLogger

# 设置上报器
setup_loguru_reporter(settings=your_settings)

# 现在IDE会正确识别report方法
logger.report("测试消息")  # ✓ 类型检查通过
```

### 可用的类型定义

- `ExtendedLogger`: 包含report方法的扩展Logger类型
- `LoggerWithReport`: ExtendedLogger的别名
- `ReportMethod`: report方法的协议定义

## 注意事项

1. **性能考虑**: 上报功能会增加一定的性能开销，建议只对重要的日志进行上报
2. **网络依赖**: 上报功能依赖网络连接，网络异常时上报可能失败
3. **异常安全**: 上报失败不会影响主程序运行，失败信息会输出到stderr
4. **配置管理**: 建议将通知渠道的token等敏感信息通过环境变量管理
5. **日志级别**: 合理设置上报的日志级别，避免产生过多的通知
6. **类型检查**: 使用提供的类型定义可以获得更好的IDE支持

## 故障排除

### 1. 上报不生效

- 检查是否正确调用了 `setup_loguru_reporter` 或 `configure_logger`
- 确认日志级别设置是否正确
- 验证通知渠道配置是否正确

### 2. 通知发送失败

- 检查网络连接
- 验证token等配置信息是否正确
- 查看stderr输出的错误信息

### 3. 性能问题

- 调整上报的日志级别，减少不必要的上报
- 考虑使用异步上报（如果支持）
- 监控上报频率，避免过于频繁的通知

## 完整示例

查看 `example/loguru_demo.py` 文件获取完整的使用示例。