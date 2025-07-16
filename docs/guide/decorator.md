# 装饰器使用指南

`@notify` 装饰器是 use-notify 的核心功能之一，它可以自动为函数执行发送通知，支持成功和失败通知。

## 基本用法

### 设置全局默认实例

```python
from use_notify import useNotify, useNotifyChannel, notify, set_default_notify_instance

# 创建并设置全局默认通知实例
default_notify = useNotify()
default_notify.add(
    useNotifyChannel.Bark({"token": "your_bark_token"}),
    useNotifyChannel.Ding({"token": "your_ding_token"})
)
set_default_notify_instance(default_notify)
```

### 简单使用

```python
# 基本使用，使用全局默认实例
@notify()
def data_processing():
    # 数据处理逻辑
    time.sleep(2)
    return "数据处理完成"

# 自定义标题
@notify(title="重要任务")
def important_task():
    return "重要任务完成"
```

## 配置参数

### 通知条件

```python
# 只在成功时通知
@notify(notify_on_success=True, notify_on_error=False)
def success_only_task():
    return "只在成功时通知"

# 只在失败时通知
@notify(notify_on_success=False, notify_on_error=True)
def error_only_task():
    if random.random() < 0.5:
        raise Exception("随机失败")
    return "成功执行"

# 禁用所有通知
@notify(notify_on_success=False, notify_on_error=False)
def silent_task():
    return "静默执行"
```

### 自定义消息模板

```python
@notify(
    success_template="✅ 任务 {function_name} 执行成功\n结果: {result}\n耗时: {execution_time:.2f}秒",
    error_template="❌ 任务 {function_name} 执行失败\n错误: {error}\n耗时: {execution_time:.2f}秒"
)
def custom_template_task():
    return "自定义模板任务完成"
```

### 包含参数和结果

```python
# 包含函数参数
@notify(include_args=True)
def task_with_args(name, count=10):
    return f"处理了 {count} 个 {name}"

# 包含函数结果
@notify(include_result=True)
def task_with_result():
    return {"status": "success", "data": [1, 2, 3]}

# 同时包含参数和结果
@notify(include_args=True, include_result=True)
def full_info_task(operation, items):
    return f"完成了 {operation}，处理了 {len(items)} 个项目"
```

### 超时设置

```python
# 设置通知发送超时时间（秒）
@notify(timeout=5)
def task_with_timeout():
    return "带超时设置的任务"
```

## 异步函数支持

```python
@notify()
async def async_data_processing():
    await asyncio.sleep(2)
    return "异步数据处理完成"

@notify(title="异步文件处理")
async def async_file_processing(file_path):
    # 模拟异步文件处理
    await asyncio.sleep(1)
    return f"文件 {file_path} 处理完成"

# 执行异步任务
result = await async_data_processing()
result = await async_file_processing("/path/to/file.txt")
```

## 模板变量

装饰器支持以下模板变量：

- `{function_name}` - 函数名称
- `{args}` - 函数参数（当 `include_args=True` 时）
- `{result}` - 函数返回值（当 `include_result=True` 时）
- `{duration}` - 函数执行时间（秒）
- `{error}` - 错误信息（失败通知时）
- `{timestamp}` - 执行时间戳

```python
@notify(
    success_template="🎉 函数 {function_name} 在 {timestamp} 执行成功\n" +
                    "参数: {args}\n" +
                    "结果: {result}\n" +
                    "耗时: {duration:.3f}秒",
    include_args=True,
    include_result=True
)
def detailed_task(name, value):
    time.sleep(1)
    return f"处理 {name}: {value}"
```

## 使用特定通知实例

```python
# 创建特定的通知实例
special_notify = useNotify()
special_notify.add(useNotifyChannel.Email({
    "smtp_server": "smtp.company.com",
    "username": "alerts@company.com",
    "password": "password",
    "to_emails": ["admin@company.com"]
}))

# 使用特定实例，覆盖全局默认实例
@notify(notify_instance=special_notify, title="系统警报")
def critical_system_check():
    # 关键系统检查
    return "系统状态正常"
```

## 实际应用场景

### 数据处理任务

```python
@notify(
    title="数据同步任务",
    success_template="✅ 数据同步完成\n处理记录数: {result}\n耗时: {execution_time:.2f}秒",
    error_template="❌ 数据同步失败\n错误: {error}",
    include_result=True
)
def sync_database():
    # 模拟数据同步
    time.sleep(3)
    processed_count = random.randint(100, 1000)
    return processed_count
```

### 文件备份任务

```python
@notify(
    title="文件备份",
    notify_on_error=True,
    notify_on_success=False,  # 只在失败时通知
    error_template="🚨 备份失败\n文件: {args}\n错误: {error}",
    include_args=True
)
def backup_file(file_path, backup_path):
    # 模拟文件备份
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"源文件不存在: {file_path}")
    
    # 执行备份逻辑
    shutil.copy2(file_path, backup_path)
    return f"备份完成: {file_path} -> {backup_path}"
```

### API 调用监控

```python
@notify(
    title="API 调用监控",
    success_template="📡 API 调用成功\nURL: {args[0]}\n响应时间: {duration:.3f}秒",
    error_template="🔥 API 调用失败\nURL: {args[0]}\n错误: {error}",
    include_args=True,
    timeout=10
)
async def call_external_api(url, data=None):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as response:
            if response.status != 200:
                raise Exception(f"HTTP {response.status}: {await response.text()}")
            return await response.json()
```

## 最佳实践

### 1. 合理设置通知条件

```python
# 对于关键任务，建议同时监控成功和失败
@notify(notify_on_success=True, notify_on_error=True)
def critical_task():
    pass

# 对于常规任务，可以只监控失败
@notify(notify_on_success=False, notify_on_error=True)
def routine_task():
    pass
```

### 2. 使用有意义的标题

```python
# 好的实践
@notify(title="用户数据导出 - 每日任务")
def export_user_data():
    pass

# 避免过于简单的标题
@notify(title="任务")
def some_task():
    pass
```

### 3. 合理使用模板变量

```python
# 包含关键信息
@notify(
    success_template="✅ {function_name} 完成\n处理时间: {execution_time:.2f}秒",
    error_template="❌ {function_name} 失败\n错误: {error}\n持续时间: {execution_time:.2f}秒"
)
def important_task():
    pass
```

### 4. 错误处理

```python
# 装饰器不会影响原函数的异常传播
@notify()
def may_fail_task():
    if random.random() < 0.5:
        raise ValueError("随机错误")
    return "成功"

# 调用时仍需要处理异常
try:
    result = may_fail_task()
except ValueError as e:
    print(f"任务失败: {e}")
```

## 调试和测试

### 禁用通知进行测试

```python
# 在测试环境中禁用通知
@notify(notify_on_success=False, notify_on_error=False)
def test_function():
    return "测试结果"
```

### 使用控制台输出进行调试

```python
from use_notify.channels import ConsoleChannel

# 创建调试用的通知实例
debug_notify = useNotify()
debug_notify.add(ConsoleChannel())

@notify(notify_instance=debug_notify)
def debug_task():
    return "调试任务"
```
