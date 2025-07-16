# @notify 装饰器使用指南

`@notify` 装饰器是 `use-notify` 库的核心功能之一，它允许您轻松地为任何函数添加通知功能，在函数执行成功或失败时自动发送通知。

## 🚀 快速开始

### 基本使用

```python
from use_notify import useNotify, useNotifyChannel, notify

# 创建通知实例
notify_instance = useNotify()
notify_instance.add(useNotifyChannel.Bark({"token": "your_bark_token"}))

# 使用装饰器
@notify(notify_instance=notify_instance)
def my_task():
    # 您的业务逻辑
    return "任务完成"

# 执行函数，自动发送通知
result = my_task()
```

### 使用全局默认实例（推荐）

为了避免每次使用装饰器都需要传递 `notify_instance` 参数，您可以设置一个全局默认实例：

```python
from use_notify import (
    useNotify, 
    useNotifyChannel, 
    notify, 
    set_default_notify_instance
)

# 创建并设置全局默认通知实例
default_notify = useNotify()
default_notify.add(useNotifyChannel.Bark({"token": "your_bark_token"}))
set_default_notify_instance(default_notify)

# 现在可以直接使用装饰器，无需传递 notify_instance
@notify()
def my_task():
    return "任务完成"

@notify(title="重要任务")
def important_task():
    return "重要任务完成"
```

### 配置方式创建通知实例

```python
from use_notify import useNotify, notify

# 使用配置字典
settings = {
    "BARK": {"token": "your_bark_token"},
    "DINGTALK": {"access_token": "your_dingtalk_token"},
    "WECHAT": {"token": "your_wechat_webhook_token"}
}

notify_instance = useNotify.from_settings(settings)

@notify(notify_instance=notify_instance)
def process_data():
    # 处理数据的逻辑
    pass
```

## 📋 配置参数

### 基本参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `notify_instance` | `Notify` | `None` | 通知实例，如果为空会创建一个空实例 |
| `title` | `str` | `"函数执行通知"` | 通知标题 |
| `notify_on_success` | `bool` | `True` | 是否在成功时发送通知 |
| `notify_on_error` | `bool` | `True` | 是否在失败时发送通知 |
| `timeout` | `float` | `30.0` | 通知发送超时时间（秒） |

### 消息模板参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `success_template` | `str` | 内置模板 | 成功通知的消息模板 |
| `error_template` | `str` | 内置模板 | 失败通知的消息模板 |
| `include_args` | `bool` | `False` | 是否在消息中包含函数参数 |
| `include_result` | `bool` | `False` | 是否在消息中包含函数返回值 |

### 模板变量

在自定义模板中，您可以使用以下变量：

- `{function_name}` - 函数名称
- `{execution_time}` - 执行时间（秒）
- `{start_time}` - 开始时间
- `{end_time}` - 结束时间
- `{args}` - 位置参数（当 `include_args=True` 时）
- `{kwargs}` - 关键字参数（当 `include_args=True` 时）
- `{result}` - 返回值（当 `include_result=True` 时）
- `{error_message}` - 错误信息（仅在失败模板中）
- `{error_type}` - 错误类型（仅在失败模板中）

## 🎯 使用场景

### 1. 数据处理任务

```python
@notify(
    notify_instance=notify_instance,
    title="数据处理任务",
    success_template="✅ 处理完成\n📊 处理了 {args[0]} 条记录\n⏱️ 耗时: {execution_time:.2f}秒",
    include_args=True
)
def process_user_data(record_count):
    # 处理用户数据
    return f"成功处理 {record_count} 条数据"
```

### 2. 文件备份任务

```python
@notify(
    notify_instance=notify_instance,
    title="文件备份",
    success_template="💾 备份完成\n📁 {args[0]} -> {args[1]}\n📋 {result}",
    include_args=True,
    include_result=True
)
def backup_files(source, target):
    # 备份文件逻辑
    return {"files_copied": 150, "total_size": "2.3GB"}
```

### 3. 异步任务

```python
@notify(
    notify_instance=notify_instance,
    title="API数据同步",
    success_template="🔄 同步完成\n📊 同步了 {result[records]} 条数据",
    include_result=True
)
async def sync_api_data():
    # 异步API调用
    await asyncio.sleep(2)
    return {"records": 500, "status": "success"}
```

### 4. 监控任务（仅失败通知）

```python
@notify(
    notify_instance=notify_instance,
    title="系统监控",
    notify_on_success=False,  # 不发送成功通知
    notify_on_error=True,     # 只发送失败通知
    error_template="🚨 监控告警\n🖥️ {args[0]}\n❗ {error_message}"
)
def health_check(service_name):
    # 健康检查逻辑
    if service_name == "database":
        raise ConnectionError("数据库连接失败")
    return "检查通过"
```

## 🌐 全局默认实例管理

### 设置默认实例

```python
from use_notify import set_default_notify_instance, useNotify, useNotifyChannel

# 创建通知实例
default_notify = useNotify()
default_notify.add(
    useNotifyChannel.Bark({"token": "bark_token"}),
    useNotifyChannel.DingTalk({"access_token": "dingtalk_token"})
)

# 设置为全局默认实例
set_default_notify_instance(default_notify)
```

### 获取当前默认实例

```python
from use_notify import get_default_notify_instance

# 获取当前的默认实例
current_default = get_default_notify_instance()
if current_default:
    print("已设置默认实例")
else:
    print("未设置默认实例")
```

### 清除默认实例

```python
from use_notify import clear_default_notify_instance

# 清除默认实例
clear_default_notify_instance()
```

### 覆盖默认实例

即使设置了全局默认实例，您仍然可以在特定的装饰器中使用不同的实例：

```python
# 设置了全局默认实例后
set_default_notify_instance(default_notify)

# 大部分函数使用默认实例
@notify()
def normal_task():
    return "普通任务"

# 特定函数使用不同的实例
special_notify = useNotify()
special_notify.add(useNotifyChannel.Email({"smtp_server": "smtp.example.com"}))

@notify(notify_instance=special_notify)  # 覆盖默认实例
def special_task():
    return "特殊任务"
```

## 🔧 高级功能

### 自定义消息格式化

```python
@notify(
    notify_instance=notify_instance,
    title="复杂任务",
    success_template=(
        "🎯 任务完成\n"
        "📋 任务: {function_name}\n"
        "📊 参数: {kwargs[task_type]}\n"
        "✅ 成功: {result[success_count]}\n"
        "❌ 失败: {result[failed_count]}\n"
        "⏱️ 耗时: {execution_time:.2f}秒"
    ),
    include_args=True,
    include_result=True
)
def complex_task(task_type="default"):
    return {
        "success_count": 95,
        "failed_count": 5,
        "total_count": 100
    }
```

### 条件通知

```python
# 只在执行时间超过阈值时通知
@notify(
    notify_instance=notify_instance,
    title="性能监控",
    success_template="⚠️ 执行时间过长: {execution_time:.2f}秒",
    notify_on_success=True,  # 可以在装饰器内部根据条件决定是否发送
)
def slow_task():
    import time
    time.sleep(5)  # 模拟耗时操作
    return "任务完成"
```

### 多通道通知

```python
# 配置多个通知渠道
notify_instance = useNotify()
notify_instance.add(
    useNotifyChannel.Bark({"token": "bark_token"}),
    useNotifyChannel.DingTalk({"access_token": "dingtalk_token"}),
    useNotifyChannel.WeChat({"token": "wechat_token"})
)

@notify(notify_instance=notify_instance)
def important_task():
    # 重要任务，通过多个渠道通知
    return "关键任务完成"
```

## 🛠️ 错误处理

装饰器具有以下错误处理特性：

1. **通知发送失败不影响原函数执行**：即使通知发送失败，原函数仍会正常执行并返回结果
2. **超时保护**：通知发送有超时机制，避免长时间阻塞
3. **异常捕获**：自动捕获并记录通知发送过程中的异常
4. **日志记录**：通知发送的错误会被记录到日志中

```python
@notify(
    notify_instance=notify_instance,
    timeout=10.0,  # 10秒超时
    error_template="🚨 任务失败\n❗ {error_message}\n🔍 错误类型: {error_type}"
)
def risky_task():
    # 可能失败的任务
    import random
    if random.random() < 0.5:
        raise ValueError("随机错误")
    return "任务成功"
```

## 📝 最佳实践

### 1. 合理使用通知

```python
# ✅ 好的做法：重要任务或长时间运行的任务
@notify(notify_instance=notify_instance)
def daily_backup():
    pass

@notify(notify_instance=notify_instance, notify_on_success=False)
def health_check():  # 只在失败时通知
    pass

# ❌ 避免：频繁执行的小任务
# @notify(notify_instance=notify_instance)
# def get_user_name(user_id):  # 这种函数不适合加通知
#     pass
```

### 2. 模板设计

```python
# ✅ 好的模板：信息丰富但简洁
success_template = (
    "✅ {function_name} 完成\n"
    "⏱️ 耗时: {execution_time:.2f}秒\n"
    "📊 结果: {result}"
)

# ❌ 避免：过于冗长的模板
# error_template = "很长很长的模板..."
```

### 3. 性能考虑

```python
# 对于异步函数，通知也是异步发送的
@notify(notify_instance=notify_instance)
async def async_task():
    await asyncio.sleep(1)
    return "异步任务完成"

# 对于同步函数，通知是同步发送的
@notify(notify_instance=notify_instance)
def sync_task():
    time.sleep(1)
    return "同步任务完成"
```

## 🔍 调试和测试

### 测试模式

```python
# 创建测试用的通知实例（不发送真实通知）
test_notify = useNotify()  # 空实例，不会发送通知

@notify(notify_instance=test_notify)
def test_function():
    return "测试结果"

# 在测试中验证函数行为
result = test_function()
assert result == "测试结果"
```

### 日志配置

```python
import logging

# 配置日志以查看通知发送情况
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('use_notify')
```

## 🚀 完整示例

查看项目中的示例文件：

- `example/decorator_demo.py` - 基础功能演示
- `example/decorator_real_usage.py` - 真实使用场景
- `tests/test_decorator.py` - 完整的测试用例

这些文件展示了装饰器的各种使用方式和最佳实践。