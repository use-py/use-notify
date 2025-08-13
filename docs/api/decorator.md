# 装饰器 API

`@notify` 装饰器是 use-notify 的核心功能之一，提供了一种优雅的方式来为函数添加通知功能。装饰器支持同步和异步函数，并提供了丰富的配置选项。

## 导入

```python
from use_notify import notify

# 或者从装饰器模块导入
from use_notify.decorator import notify
```

## 基本语法

```python
@notify(notify_instance=None, **kwargs)
def your_function():
    pass
```

## 参数说明

### `notify_instance`

指定用于发送通知的 `useNotify` 实例。

**类型**: `useNotify` 或 `None`  
**默认值**: `None` (使用全局默认实例)  
**说明**: 如果为 `None`，将使用通过 `set_default_notify()` 设置的全局默认实例

```python
from use_notify import useNotify, useNotifyChannel, notify

# 创建特定的通知实例
custom_notify = useNotify()
custom_notify.add(useNotifyChannel.Bark({"token": "custom_token"}))

# 使用特定实例
@notify(notify_instance=custom_notify)
def task_with_custom_notify():
    return "使用自定义通知实例"

# 使用全局默认实例
@notify()  # notify_instance=None
def task_with_default_notify():
    return "使用全局默认实例"
```

### `title`

通知标题模板。

**类型**: `str` 或 `None`  
**默认值**: `None` (自动生成)  
**支持模板变量**: 是

```python
# 固定标题
@notify(title="任务完成")
def simple_task():
    return "完成"

# 模板标题
@notify(title="函数 {function_name} 执行完成")
def template_task():
    return "结果"

# 包含参数的标题
@notify(title="处理用户 {args[0]} 的数据")
def process_user(user_id):
    return f"处理用户 {user_id}"

# 包含关键字参数的标题
@notify(title="备份 {kwargs[database]} 数据库")
def backup_database(database="main"):
    return "备份完成"
```

### `on_success`

函数成功执行时是否发送通知。

**类型**: `bool`  
**默认值**: `True`

```python
# 只在成功时通知
@notify(on_success=True, on_failure=False)
def success_only_task():
    return "成功"

# 不在成功时通知
@notify(on_success=False, on_failure=True)
def failure_only_task():
    if random.random() < 0.5:
        raise Exception("随机失败")
    return "成功"
```

### `on_failure`

函数执行失败时是否发送通知。

**类型**: `bool`  
**默认值**: `True`

```python
# 成功和失败都通知
@notify(on_success=True, on_failure=True)
def both_notify_task():
    if random.random() < 0.3:
        raise Exception("随机失败")
    return "成功"

# 只在失败时通知
@notify(on_success=False, on_failure=True)
def error_monitor_task():
    # 监控任务，只关心错误
    critical_operation()
    return "操作完成"
```

### `include_args`

是否在通知内容中包含函数参数。

**类型**: `bool`  
**默认值**: `False`

```python
@notify(include_args=True)
def process_data(data_id, format="json", validate=True):
    # 通知内容将包含: data_id=123, format=json, validate=True
    return f"处理数据 {data_id}"

# 调用示例
process_data(123, format="xml", validate=False)
```

### `include_result`

是否在通知内容中包含函数返回值。

**类型**: `bool`  
**默认值**: `False`

```python
@notify(include_result=True)
def calculate_sum(a, b):
    result = a + b
    # 通知内容将包含返回值: 15
    return result

# 调用示例
calculate_sum(7, 8)  # 通知中会显示结果: 15
```

### `success_template`

成功时的通知内容模板。

**类型**: `str` 或 `None`  
**默认值**: `None` (使用默认模板)  
**支持模板变量**: 是

```python
@notify(
    success_template="✅ 函数 {function_name} 成功执行\n参数: {args}\n结果: {result}\n耗时: {execution_time:.2f}秒"
)
def detailed_task(task_name):
    time.sleep(1)  # 模拟耗时操作
    return f"任务 {task_name} 完成"

# 自定义成功模板
@notify(
    success_template="🎉 {function_name} 执行成功！\n📊 处理了 {result} 条记录"
)
def process_records():
    # 模拟处理记录
    processed = random.randint(100, 1000)
    return processed
```

### `failure_template`

失败时的通知内容模板。

**类型**: `str` 或 `None`  
**默认值**: `None` (使用默认模板)  
**支持模板变量**: 是

```python
@notify(
    failure_template="❌ 函数 {function_name} 执行失败\n错误: {error}\n参数: {args}\n耗时: {execution_time:.2f}秒"
)
def risky_task(operation):
    if operation == "dangerous":
        raise ValueError("危险操作被拒绝")
    return "操作完成"

# 包含错误详情的模板
@notify(
    failure_template="🚨 严重错误\n函数: {function_name}\n错误类型: {error_type}\n错误信息: {error}\n发生时间: {current_time}"
)
def critical_operation():
    # 可能失败的关键操作
    if random.random() < 0.3:
        raise RuntimeError("系统资源不足")
    return "操作成功"
```

### `timeout`

函数执行超时时间（秒）。

**类型**: `float` 或 `None`  
**默认值**: `None` (无超时限制)  
**说明**: 仅对异步函数有效

```python
import asyncio

@notify(timeout=5.0)  # 5秒超时
async def async_task_with_timeout():
    await asyncio.sleep(3)  # 正常完成
    return "任务完成"

@notify(timeout=2.0)  # 2秒超时
async def slow_async_task():
    await asyncio.sleep(5)  # 会超时
    return "不会到达这里"

# 使用示例
async def main():
    try:
        result1 = await async_task_with_timeout()  # 正常完成
        print(result1)
    except asyncio.TimeoutError:
        print("任务1超时")
    
    try:
        result2 = await slow_async_task()  # 会超时
        print(result2)
    except asyncio.TimeoutError:
        print("任务2超时")

asyncio.run(main())
```

## 模板变量

装饰器支持在 `title`、`success_template` 和 `failure_template` 中使用以下模板变量：

### 基础变量

| 变量 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `function_name` | str | 函数名称 | `"process_data"` |
| `args` | tuple | 位置参数 | `(1, 2, 3)` |
| `kwargs` | dict | 关键字参数 | `{"format": "json"}` |
| `execution_time` | float | 执行耗时（秒） | `1.23` |
| `start_time` | str | 函数开始执行时间 | `"2024-01-01 12:00:00"` |
| `end_time` | str | 函数结束执行时间 | `"2024-01-01 12:00:01"` |
| `current_time` | str | 发送通知时的当前时间 | `"2024-01-01 12:00:01"` |

### 成功时可用变量

| 变量 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `result` | any | 函数返回值 | `"处理完成"` |
| `status` | str | 执行状态 | `"success"` |

### 失败时可用变量

| 变量 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `error` | str | 错误信息 | `"文件不存在"` |
| `error_type` | str | 错误类型 | `"FileNotFoundError"` |
| `status` | str | 执行状态 | `"failure"` |

### 模板变量使用示例

```python
@notify(
    title="{function_name} 开始执行",
    success_template="""
✅ 执行成功
📋 函数: {function_name}
⏱️ 耗时: {execution_time:.2f}秒
📥 参数: {args}
📤 结果: {result}
🕐 开始时间: {start_time}
🕐 结束时间: {end_time}
🕐 通知时间: {current_time}
""",
    failure_template="""
❌ 执行失败
📋 函数: {function_name}
⏱️ 耗时: {execution_time:.2f}秒
📥 参数: {args}
🚨 错误: {error_message}
🕐 开始时间: {start_time}
🕐 结束时间: {end_time}
🕐 通知时间: {current_time}
""",
    include_args=True,
    include_result=True
)
def comprehensive_task(task_id, config=None):
    """综合示例任务"""
    if task_id < 0:
        raise ValueError("任务ID不能为负数")
    
    # 模拟处理
    time.sleep(0.5)
    
    return {
        "task_id": task_id,
        "status": "completed",
        "processed_items": random.randint(10, 100)
    }

# 时间变量对比示例
@notify(
    success_template="""
⏰ 时间信息对比:
🟢 开始时间: {start_time}
🔴 结束时间: {end_time}
🔵 通知时间: {current_time}
💡 说明: current_time 通常会比 end_time 稍晚，因为它是在格式化通知消息时获取的
"""
)
def time_demo_task():
    """演示时间变量的任务"""
    time.sleep(1)
    return "任务完成"

# 调用示例
comprehensive_task(123, config={"mode": "fast"})
```

### 时间变量详解

在通知模板中，有三个与时间相关的变量，它们的含义和使用场景略有不同：

| 变量 | 获取时机 | 说明 | 使用场景 |
|------|----------|------|----------|
| `start_time` | 函数开始执行时 | 记录函数开始执行的准确时间 | 用于显示任务开始时间，计算总耗时 |
| `end_time` | 函数执行完成时 | 记录函数执行完成的准确时间 | 用于显示任务结束时间，计算总耗时 |
| `current_time` | 格式化通知消息时 | 记录发送通知时的当前时间 | 用于显示通知发送时间，可能略晚于end_time |

#### 时间差异说明

- `start_time` 和 `end_time` 是函数执行过程中记录的时间戳
- `current_time` 是在格式化通知消息时实时获取的时间
- 通常 `current_time` 会比 `end_time` 稍晚几毫秒，因为中间还有消息格式化的处理时间
- 如果通知渠道有延迟（如网络请求），`current_time` 仍然是格式化时的时间，不是实际发送成功的时间

#### 使用建议

```python
# 显示任务执行时间范围
@notify(
    success_template="任务执行时间: {start_time} - {end_time}"
)

# 显示通知发送时间
@notify(
    success_template="通知发送时间: {current_time}"
)

# 完整的时间信息
@notify(
    success_template="""
📅 执行时间: {start_time} - {end_time}
⏱️ 执行耗时: {execution_time:.2f}秒
📤 通知时间: {current_time}
"""
)
```

## 使用示例

### 基本用法

```python
from use_notify import useNotify, useNotifyChannel, notify, set_default_notify

# 设置全局默认通知实例
default_notify = useNotify()
default_notify.add(useNotifyChannel.Bark({"token": "your_token"}))
set_default_notify(default_notify)

# 基本装饰器使用
@notify()
def simple_task():
    """简单任务"""
    time.sleep(1)
    return "任务完成"

# 自定义标题
@notify(title="数据处理任务")
def process_data():
    """处理数据"""
    # 模拟数据处理
    processed = random.randint(100, 1000)
    return f"处理了 {processed} 条记录"

# 只在失败时通知
@notify(on_success=False, on_failure=True, title="错误监控")
def monitor_system():
    """系统监控"""
    if random.random() < 0.1:  # 10% 概率失败
        raise Exception("系统异常")
    return "系统正常"

# 执行任务
simple_task()
process_data()
monitor_system()
```

### 异步函数支持

```python
import asyncio
from use_notify import notify

@notify(title="异步任务: {function_name}")
async def async_data_fetch(url):
    """异步获取数据"""
    # 模拟异步HTTP请求
    await asyncio.sleep(2)
    return f"从 {url} 获取的数据"

@notify(
    timeout=5.0,
    success_template="✅ 异步任务完成\n结果: {result}\n耗时: {execution_time:.2f}秒",
    failure_template="❌ 异步任务失败\n错误: {error}\n耗时: {execution_time:.2f}秒"
)
async def async_task_with_timeout():
    """带超时的异步任务"""
    await asyncio.sleep(3)
    return "异步处理完成"

# 运行异步任务
async def main():
    result1 = await async_data_fetch("https://api.example.com/data")
    print(result1)
    
    result2 = await async_task_with_timeout()
    print(result2)

asyncio.run(main())
```

### 条件通知

```python
from use_notify import notify

class ConditionalNotifyDecorator:
    """条件通知装饰器类"""
    
    @staticmethod
    def notify_on_error_level(level="warning"):
        """根据错误级别决定是否通知"""
        def decorator(func):
            @notify(
                on_success=False,
                on_failure=True,
                title=f"[{level.upper()}] {func.__name__} 失败"
            )
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    # 根据错误级别决定是否重新抛出
                    if level in ["error", "critical"]:
                        raise
                    else:
                        print(f"警告: {e}")
                        return None
            return wrapper
        return decorator
    
    @staticmethod
    def notify_on_duration(min_duration=1.0):
        """只有当执行时间超过阈值时才通知"""
        def decorator(func):
            @notify(
            title="长时间运行任务: {function_name}",
            success_template="⏰ 任务完成\n耗时: {execution_time:.2f}秒 (超过 {min_duration}秒)"
        )
            def wrapper(*args, **kwargs):
                start_time = time.time()
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                # 只有超过最小时长才发送通知
                if duration >= min_duration:
                    # 这里可以手动触发通知
                    pass
                
                return result
            return wrapper
        return decorator

# 使用条件通知
@ConditionalNotifyDecorator.notify_on_error_level("error")
def critical_operation():
    """关键操作"""
    if random.random() < 0.2:
        raise RuntimeError("关键操作失败")
    return "操作成功"

@ConditionalNotifyDecorator.notify_on_duration(2.0)
def potentially_slow_task():
    """可能很慢的任务"""
    sleep_time = random.uniform(0.5, 3.0)
    time.sleep(sleep_time)
    return f"任务完成，耗时 {sleep_time:.2f} 秒"
```

### 多实例通知

```python
from use_notify import useNotify, useNotifyChannel, notify

# 创建不同的通知实例
# 开发环境通知
dev_notify = useNotify()
dev_notify.add(useNotifyChannel.Bark({"token": "dev_token"}))

# 生产环境通知
prod_notify = useNotify()
prod_notify.add(useNotifyChannel.Ding({"token": "prod_ding_token"}))
prod_notify.add(useNotifyChannel.Email({
    "smtp_server": "smtp.company.com",
    "smtp_port": 587,
    "username": "alerts@company.com",
    "password": "password",
    "to_emails": ["ops@company.com"]
}))

# 根据环境选择通知实例
import os
ENVIRONMENT = os.getenv("ENVIRONMENT", "dev")
notify_instance = prod_notify if ENVIRONMENT == "prod" else dev_notify

@notify(
    notify_instance=notify_instance,
    title="[{env}] 部署任务".format(env=ENVIRONMENT.upper())
)
def deploy_application(version):
    """部署应用"""
    print(f"部署版本 {version} 到 {ENVIRONMENT} 环境")
    
    # 模拟部署过程
    time.sleep(2)
    
    if ENVIRONMENT == "prod" and random.random() < 0.1:
        raise Exception("生产环境部署失败")
    
    return f"版本 {version} 部署成功"

# 执行部署
deploy_application("v2.1.0")
```

### 装饰器链

```python
from functools import wraps
from use_notify import notify

def retry(max_attempts=3, delay=1):
    """重试装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        print(f"尝试 {attempt + 1} 失败，{delay}秒后重试")
                        time.sleep(delay)
                    else:
                        print(f"所有 {max_attempts} 次尝试都失败了")
            raise last_exception
        return wrapper
    return decorator

def timing(func):
    """计时装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start
            print(f"{func.__name__} 执行成功，耗时 {execution_time:.2f} 秒")
            return result
        except Exception as e:
            duration = time.time() - start
            print(f"{func.__name__} 执行失败，耗时 {execution_time:.2f} 秒，错误: {e}")
            raise
    return wrapper

# 装饰器链：通知 -> 重试 -> 计时
@notify(
    title="重要任务: {function_name}",
    success_template="✅ 任务成功 (尝试了 {retry_count} 次)",
    failure_template="❌ 任务最终失败 (尝试了 {max_attempts} 次)"
)
@retry(max_attempts=3, delay=2)
@timing
def important_task_with_retry():
    """重要的可能失败的任务"""
    if random.random() < 0.7:  # 70% 概率失败
        raise Exception("任务执行失败")
    return "任务成功完成"

# 执行任务
important_task_with_retry()
```

### 类方法装饰

```python
from use_notify import notify

class DataProcessor:
    """数据处理器类"""
    
    def __init__(self, name):
        self.name = name
        self.processed_count = 0
    
    @notify(
        title="{self.name} 开始处理数据",
        success_template="✅ {self.name} 处理完成\n本次处理: {result} 条\n总计处理: {self.processed_count} 条"
    )
    def process_batch(self, batch_size=100):
        """批量处理数据"""
        # 模拟数据处理
        time.sleep(1)
        
        if random.random() < 0.1:  # 10% 概率失败
            raise Exception("数据处理失败")
        
        processed = random.randint(batch_size - 10, batch_size + 10)
        self.processed_count += processed
        
        return processed
    
    @notify(
        title="{self.name} 生成报告",
        include_result=True
    )
    def generate_report(self):
        """生成处理报告"""
        return {
            "processor": self.name,
            "total_processed": self.processed_count,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }

# 使用类实例
processor = DataProcessor("数据处理器-01")
processor.process_batch(150)
processor.process_batch(200)
report = processor.generate_report()
print(report)
```

## 最佳实践

### 1. 合理设置通知条件

```python
# ✅ 好的做法：只在重要事件时通知
@notify(on_success=False, on_failure=True)  # 只关心失败
def critical_system_check():
    pass

@notify(on_success=True, on_failure=True)   # 成功和失败都关心
def important_business_process():
    pass

# ❌ 避免：高频函数的成功通知
@notify(on_success=True)  # 会产生大量通知
def frequently_called_function():
    pass
```

### 2. 使用有意义的标题和模板

```python
# ✅ 好的做法：描述性标题
@notify(title="用户数据备份 - {kwargs[database]}")
def backup_user_data(database="main"):
    pass

@notify(
    title="订单处理",
    success_template="✅ 订单 {args[0]} 处理成功\n金额: ¥{result[amount]}\n状态: {result[status]}"
)
def process_order(order_id):
    return {"amount": 299.99, "status": "completed"}

# ❌ 避免：无意义的标题
@notify(title="函数执行")
def some_function():
    pass
```

### 3. 适当使用参数和结果包含

```python
# ✅ 好的做法：敏感操作包含参数
@notify(
    include_args=True,
    title="安全操作: {function_name}"
)
def security_operation(user_id, action):
    pass

# ✅ 好的做法：重要结果包含返回值
@notify(
    include_result=True,
    title="数据分析完成"
)
def analyze_data():
    return {"insights": ["趋势上升", "异常检测"], "confidence": 0.95}

# ❌ 避免：包含敏感信息
@notify(include_args=True)  # 可能暴露密码等敏感信息
def login(username, password):
    pass
```

### 4. 错误处理和降级

```python
from use_notify import notify
from use_notify.exceptions import NotifySendError

@notify(
    on_failure=True,
    failure_template="🚨 关键任务失败: {error}"
)
def critical_task_with_fallback():
    """关键任务，带降级处理"""
    try:
        # 主要逻辑
        return perform_critical_operation()
    except Exception as e:
        # 降级逻辑
        print(f"主要操作失败: {e}，执行降级方案")
        return perform_fallback_operation()

def safe_notify_wrapper(func):
    """安全的通知包装器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except NotifySendError as e:
            # 通知发送失败，记录日志但不影响主要功能
            print(f"通知发送失败: {e}")
            return func.__wrapped__(*args, **kwargs)
    return wrapper

@safe_notify_wrapper
@notify(title="安全包装的任务")
def safely_wrapped_task():
    return "任务完成"
```

### 5. 测试和调试

```python
import os
from use_notify import notify, set_default_notify, useNotify

# 测试模式：禁用通知
if os.getenv("TESTING") == "true":
    # 创建一个不发送通知的实例
    test_notify = useNotify()  # 不添加任何渠道
    set_default_notify(test_notify)

@notify(
    title="测试任务",
    success_template="测试成功: {result}"
)
def testable_function():
    """可测试的函数"""
    return "测试结果"

# 单元测试
def test_function():
    """单元测试"""
    result = testable_function()
    assert result == "测试结果"
    print("测试通过")

# 调试模式：详细通知
if os.getenv("DEBUG") == "true":
    @notify(
        include_args=True,
        include_result=True,
        success_template="🐛 调试信息\n函数: {function_name}\n参数: {args}\n结果: {result}\n耗时: {execution_time:.3f}秒"
    )
    def debug_function(param1, param2="default"):
        return f"处理 {param1} 和 {param2}"
else:
    @notify(title="生产任务")
    def debug_function(param1, param2="default"):
        return f"处理 {param1} 和 {param2}"
```

通过合理使用 `@notify` 装饰器的各种参数和特性，您可以为应用程序添加强大而灵活的通知功能，提高系统的可观测性和运维效率。
