# 快速开始

本指南将帮助您快速开始使用 use-notify。

## 安装

使用 pip 安装 use-notify：

```bash
pip install use-notify
```

## 基本使用

### 创建通知实例

```python
from use_notify import useNotify, useNotifyChannel

# 创建通知实例
notify = useNotify()

# 添加通知渠道
notify.add(
    useNotifyChannel.Bark({"token": "your_bark_token"}),
    useNotifyChannel.Ding({
        "token": "your_ding_token",
        "at_all": True
    }),
    useNotifyChannel.Email({
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
        "username": "your_email@gmail.com",
        "password": "your_password",
        "to_emails": ["recipient@example.com"]
    })
)
```

### 发送通知

```python
# 发送基本通知
notify.publish(title="消息标题", content="消息正文")

# 异步发送通知
await notify.publish_async(title="异步消息", content="异步消息正文")
```

## 装饰器使用

### 设置全局默认实例

```python
from use_notify import notify, set_default_notify_instance

# 设置全局默认通知实例
set_default_notify_instance(notify)
```

### 基本装饰器用法

```python
# 基本使用
@notify()
def data_processing():
    # 数据处理逻辑
    time.sleep(2)
    return "数据处理完成"

# 自定义标题
@notify(title="重要任务")
def important_task():
    return "重要任务完成"

# 只在出错时通知
@notify(notify_on_error=True, notify_on_success=False)
def risky_operation():
    if random.random() < 0.5:
        raise Exception("操作失败")
    return "操作成功"
```

### 异步函数支持

```python
@notify()
async def async_task():
    await asyncio.sleep(2)
    return "异步任务完成"

# 执行异步任务
result = await async_task()
```

## 自定义消息模板

```python
@notify(
    success_template="✅ 任务 {function_name} 执行成功\n结果: {result}\n耗时: {duration:.2f}秒",
    error_template="❌ 任务 {function_name} 执行失败\n错误: {error}\n耗时: {duration:.2f}秒"
)
def custom_template_task():
    return "自定义模板任务完成"
```

## 错误处理

use-notify 的设计原则是通知发送失败不应影响原函数的执行：

```python
@notify()
def important_business_logic():
    # 即使通知发送失败，这个函数仍会正常执行
    return "业务逻辑执行完成"

# 函数会正常执行，即使通知渠道配置错误
result = important_business_logic()
print(result)  # 输出: 业务逻辑执行完成
```

## 下一步

- 了解更多[装饰器功能](decorator)详细用法
- 探索[通知渠道](channels)配置方法
- 查看[配置管理](configuration)最佳实践
- 学习[最佳实践](best-practices)指南
