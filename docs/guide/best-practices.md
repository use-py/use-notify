# 最佳实践

本指南总结了使用 use-notify 的最佳实践，帮助您构建可靠、高效、易维护的通知系统。

## 通知设计原则

### 1. 合理的通知频率

```python
import time
from datetime import datetime, timedelta
from use_notify import useNotify, set_default_notify_instance

class RateLimitedNotify:
    """限制通知频率的包装器"""
    
    def __init__(self, notify_instance, min_interval=300):  # 默认5分钟间隔
        self.notify = notify_instance
        self.min_interval = min_interval
        self.last_sent = {}
    
    def should_send(self, key):
        """检查是否应该发送通知"""
        now = datetime.now()
        if key not in self.last_sent:
            return True
        
        time_diff = (now - self.last_sent[key]).total_seconds()
        return time_diff >= self.min_interval
    
    def send_if_needed(self, title, content, key=None):
        """根据频率限制发送通知"""
        if key is None:
            key = f"{title}:{content}"
        
        if self.should_send(key):
            self.notify.publish(title=title, content=content)
            self.last_sent[key] = datetime.now()
            return True
        return False

# 使用示例
notify = useNotify()
rate_limited_notify = RateLimitedNotify(notify, min_interval=600)  # 10分钟间隔

# 在监控中使用
def check_system_health():
    cpu_usage = get_cpu_usage()
    if cpu_usage > 80:
        rate_limited_notify.send_if_needed(
            title="系统警报",
            content=f"CPU使用率过高: {cpu_usage}%",
            key="high_cpu_usage"  # 使用固定key避免重复通知
        )
```

### 2. 智能通知条件

```python
from use_notify import notify

# ✅ 推荐：只在重要情况下通知
@notify(condition=lambda result: result.get('error_count', 0) > 0)
def process_data(data):
    errors = []
    for item in data:
        try:
            process_item(item)
        except Exception as e:
            errors.append(str(e))
    
    return {
        'processed': len(data) - len(errors),
        'error_count': len(errors),
        'errors': errors
    }

# ✅ 推荐：根据结果严重程度决定是否通知
@notify(
    condition=lambda result: result.get('severity') in ['error', 'critical'],
    title=lambda result: f"[{result.get('severity', 'info').upper()}] 系统检查"
)
def system_check():
    issues = check_system_issues()
    severity = 'info'
    
    if any(issue['level'] == 'critical' for issue in issues):
        severity = 'critical'
    elif any(issue['level'] == 'error' for issue in issues):
        severity = 'error'
    elif any(issue['level'] == 'warning' for issue in issues):
        severity = 'warning'
    
    return {
        'severity': severity,
        'issues': issues,
        'timestamp': datetime.now().isoformat()
    }

# ❌ 避免：过于频繁的通知
@notify()  # 每次调用都通知
def log_user_action(action):
    return f"用户执行了: {action}"
```

### 3. 有意义的通知内容

```python
# ✅ 推荐：提供详细且有用的信息
@notify(
    title="数据备份完成",
    content_template="备份了 {processed_files} 个文件，总大小 {total_size}，耗时 {duration}秒。\n备份路径: {backup_path}"
)
def backup_data():
    start_time = time.time()
    files = get_files_to_backup()
    backup_path = create_backup(files)
    
    return {
        'processed_files': len(files),
        'total_size': format_file_size(sum(get_file_size(f) for f in files)),
        'duration': round(time.time() - start_time, 2),
        'backup_path': backup_path
    }

# ✅ 推荐：包含上下文信息
@notify(
    title=lambda result: f"API调用{'成功' if result['success'] else '失败'}",
    content_template="""API: {api_name}
状态: {status_code}
响应时间: {response_time}ms
{error_info}"""
)
def call_external_api(api_name, url):
    start_time = time.time()
    try:
        response = requests.get(url, timeout=30)
        response_time = round((time.time() - start_time) * 1000, 2)
        
        return {
            'success': response.status_code == 200,
            'api_name': api_name,
            'status_code': response.status_code,
            'response_time': response_time,
            'error_info': '' if response.status_code == 200 else f'错误: {response.text}'
        }
    except Exception as e:
        response_time = round((time.time() - start_time) * 1000, 2)
        return {
            'success': False,
            'api_name': api_name,
            'status_code': 'N/A',
            'response_time': response_time,
            'error_info': f'异常: {str(e)}'
        }
```

## 性能优化

### 1. 异步通知

```python
import asyncio
from use_notify import notify

# ✅ 推荐：对于I/O密集型任务使用异步
@notify(title="异步数据处理完成")
async def process_large_dataset(dataset):
    """异步处理大数据集"""
    results = []
    
    # 并发处理多个数据块
    tasks = []
    for chunk in split_dataset(dataset, chunk_size=1000):
        task = asyncio.create_task(process_chunk_async(chunk))
        tasks.append(task)
    
    chunk_results = await asyncio.gather(*tasks)
    
    for result in chunk_results:
        results.extend(result)
    
    return {
        'processed_count': len(results),
        'success_count': sum(1 for r in results if r['success']),
        'error_count': sum(1 for r in results if not r['success'])
    }

# ✅ 推荐：批量处理通知
class BatchNotify:
    """批量通知处理器"""
    
    def __init__(self, notify_instance, batch_size=10, flush_interval=60):
        self.notify = notify_instance
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.pending_notifications = []
        self.last_flush = time.time()
    
    def add_notification(self, title, content):
        """添加通知到批次"""
        self.pending_notifications.append({
            'title': title,
            'content': content,
            'timestamp': datetime.now()
        })
        
        # 检查是否需要刷新
        if (len(self.pending_notifications) >= self.batch_size or 
            time.time() - self.last_flush >= self.flush_interval):
            self.flush()
    
    def flush(self):
        """发送批量通知"""
        if not self.pending_notifications:
            return
        
        # 合并通知内容
        summary_title = f"批量通知 ({len(self.pending_notifications)} 条)"
        summary_content = "\n\n".join([
            f"[{notif['timestamp'].strftime('%H:%M:%S')}] {notif['title']}\n{notif['content']}"
            for notif in self.pending_notifications
        ])
        
        self.notify.publish(title=summary_title, content=summary_content)
        
        self.pending_notifications.clear()
        self.last_flush = time.time()

# 使用批量通知
batch_notify = BatchNotify(notify)

def log_event(event_type, details):
    batch_notify.add_notification(
        title=f"事件: {event_type}",
        content=details
    )
```

### 2. 连接池和重用

```python
from use_notify import useNotify, useNotifyChannel
import threading

class OptimizedNotifyManager:
    """优化的通知管理器"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.notify = useNotify()
        self._setup_channels()
        self._initialized = True
    
    def _setup_channels(self):
        """设置优化的通知渠道"""
        # 使用连接池的邮件配置
        email_config = {
            "smtp_server": os.getenv("SMTP_SERVER"),
            "smtp_port": int(os.getenv("SMTP_PORT", "587")),
            "username": os.getenv("EMAIL_USERNAME"),
            "password": os.getenv("EMAIL_PASSWORD"),
            "to_emails": os.getenv("EMAIL_RECIPIENTS", "").split(","),
            "pool_size": 5,  # 连接池大小
            "max_retries": 3  # 最大重试次数
        }
        
        self.notify.add(
            useNotifyChannel.Email(email_config),
            useNotifyChannel.Bark({"token": os.getenv("BARK_TOKEN")}),
            useNotifyChannel.Ding({"token": os.getenv("DING_TOKEN")})
        )
    
    def send_notification(self, title, content, priority='normal'):
        """发送通知"""
        try:
            if priority == 'high':
                # 高优先级通知使用所有渠道
                self.notify.publish(title=title, content=content)
            else:
                # 普通通知只使用轻量级渠道
                bark_notify = useNotify()
                bark_notify.add(useNotifyChannel.Bark({"token": os.getenv("BARK_TOKEN")}))
                bark_notify.publish(title=title, content=content)
        except Exception as e:
            print(f"通知发送失败: {e}")

# 使用单例模式的通知管理器
notify_manager = OptimizedNotifyManager()
```

## 错误处理和可靠性

### 1. 优雅的错误处理

```python
from use_notify import notify
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ✅ 推荐：完善的错误处理
@notify(
    title="任务执行结果",
    condition=lambda result: result is not None,  # 只在有结果时通知
    content_template="""任务: {task_name}
状态: {status}
{details}
执行时间: {execution_time}秒"""
)
def robust_task(task_name, *args, **kwargs):
    """健壮的任务执行"""
    start_time = time.time()
    
    try:
        # 执行实际任务
        result = execute_task(task_name, *args, **kwargs)
        
        execution_time = round(time.time() - start_time, 2)
        
        return {
            'task_name': task_name,
            'status': '成功',
            'details': f'处理了 {result.get("count", 0)} 项数据',
            'execution_time': execution_time,
            'result': result
        }
        
    except Exception as e:
        execution_time = round(time.time() - start_time, 2)
        
        # 记录错误日志
        logger.error(f"任务 {task_name} 执行失败: {e}", exc_info=True)
        
        return {
            'task_name': task_name,
            'status': '失败',
            'details': f'错误: {str(e)}',
            'execution_time': execution_time,
            'error': str(e)
        }

# ✅ 推荐：重试机制
class RetryableNotify:
    """支持重试的通知"""
    
    def __init__(self, notify_instance, max_retries=3, retry_delay=1):
        self.notify = notify_instance
        self.max_retries = max_retries
        self.retry_delay = retry_delay
    
    def send_with_retry(self, title, content):
        """带重试的发送通知"""
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                self.notify.publish(title=title, content=content)
                if attempt > 0:
                    logger.info(f"通知在第 {attempt + 1} 次尝试后发送成功")
                return True
                
            except Exception as e:
                last_exception = e
                logger.warning(f"通知发送失败 (尝试 {attempt + 1}/{self.max_retries + 1}): {e}")
                
                if attempt < self.max_retries:
                    time.sleep(self.retry_delay * (2 ** attempt))  # 指数退避
        
        logger.error(f"通知发送最终失败: {last_exception}")
        return False

# 使用重试通知
retryable_notify = RetryableNotify(notify)

@notify(
    title="关键任务完成",
    notify_instance=retryable_notify
)
def critical_task():
    return "关键任务执行完成"
```

### 2. 降级策略

```python
class FallbackNotify:
    """支持降级的通知系统"""
    
    def __init__(self):
        self.primary_notify = self._create_primary_notify()
        self.fallback_notify = self._create_fallback_notify()
        self.emergency_notify = self._create_emergency_notify()
    
    def _create_primary_notify(self):
        """创建主要通知渠道"""
        notify = useNotify()
        notify.add(
            useNotifyChannel.Ding({"token": os.getenv("DING_TOKEN")}),
            useNotifyChannel.Email({
                "smtp_server": "smtp.company.com",
                "smtp_port": 587,
                "username": os.getenv("EMAIL_USERNAME"),
                "password": os.getenv("EMAIL_PASSWORD"),
                "to_emails": [os.getenv("EMAIL_RECIPIENT")]
            })
        )
        return notify
    
    def _create_fallback_notify(self):
        """创建备用通知渠道"""
        notify = useNotify()
        notify.add(useNotifyChannel.Bark({"token": os.getenv("BARK_TOKEN")}))
        return notify
    
    def _create_emergency_notify(self):
        """创建紧急通知渠道（本地日志）"""
        class LogChannel:
            def send(self, title, content, **kwargs):
                logger.critical(f"[紧急通知] {title}: {content}")
                return True
            
            async def send_async(self, title, content, **kwargs):
                return self.send(title, content, **kwargs)
        
        notify = useNotify()
        notify.add(LogChannel())
        return notify
    
    def send_notification(self, title, content, level='normal'):
        """发送通知，支持降级"""
        notifiers = [self.primary_notify, self.fallback_notify, self.emergency_notify]
        
        for i, notifier in enumerate(notifiers):
            try:
                notifier.publish(title=title, content=content)
                if i > 0:
                    logger.warning(f"使用了第 {i + 1} 级通知渠道")
                return True
            except Exception as e:
                logger.error(f"第 {i + 1} 级通知渠道失败: {e}")
                continue
        
        logger.critical("所有通知渠道都失败了")
        return False

# 使用降级通知
fallback_notify = FallbackNotify()
```

## 监控和调试

### 1. 通知统计

```python
from collections import defaultdict, Counter
from datetime import datetime, timedelta

class NotifyStats:
    """通知统计"""
    
    def __init__(self):
        self.stats = {
            'total_sent': 0,
            'total_failed': 0,
            'by_channel': defaultdict(lambda: {'sent': 0, 'failed': 0}),
            'by_hour': defaultdict(int),
            'recent_notifications': [],
            'error_log': []
        }
    
    def record_sent(self, channel_name, title, content):
        """记录发送成功"""
        self.stats['total_sent'] += 1
        self.stats['by_channel'][channel_name]['sent'] += 1
        
        hour = datetime.now().hour
        self.stats['by_hour'][hour] += 1
        
        self.stats['recent_notifications'].append({
            'timestamp': datetime.now(),
            'channel': channel_name,
            'title': title,
            'status': 'sent'
        })
        
        # 只保留最近100条记录
        if len(self.stats['recent_notifications']) > 100:
            self.stats['recent_notifications'] = self.stats['recent_notifications'][-100:]
    
    def record_failed(self, channel_name, title, error):
        """记录发送失败"""
        self.stats['total_failed'] += 1
        self.stats['by_channel'][channel_name]['failed'] += 1
        
        self.stats['error_log'].append({
            'timestamp': datetime.now(),
            'channel': channel_name,
            'title': title,
            'error': str(error)
        })
        
        # 只保留最近50条错误记录
        if len(self.stats['error_log']) > 50:
            self.stats['error_log'] = self.stats['error_log'][-50:]
    
    def get_summary(self):
        """获取统计摘要"""
        total = self.stats['total_sent'] + self.stats['total_failed']
        success_rate = (self.stats['total_sent'] / total * 100) if total > 0 else 0
        
        return {
            'total_notifications': total,
            'success_rate': round(success_rate, 2),
            'total_sent': self.stats['total_sent'],
            'total_failed': self.stats['total_failed'],
            'by_channel': dict(self.stats['by_channel']),
            'peak_hour': max(self.stats['by_hour'].items(), key=lambda x: x[1])[0] if self.stats['by_hour'] else None
        }

# 集成统计功能的通知包装器
class MonitoredNotify:
    """带监控的通知"""
    
    def __init__(self, notify_instance):
        self.notify = notify_instance
        self.stats = NotifyStats()
    
    def publish(self, title, content, **kwargs):
        """发送通知并记录统计"""
        try:
            result = self.notify.publish(title=title, content=content, **kwargs)
            self.stats.record_sent('mixed', title, content)
            return result
        except Exception as e:
            self.stats.record_failed('mixed', title, e)
            raise
    
    def get_stats(self):
        """获取统计信息"""
        return self.stats.get_summary()

# 使用监控通知
monitored_notify = MonitoredNotify(notify)

# 定期报告统计信息
@notify(
    title="通知系统统计报告",
    content_template="""统计周期: 过去24小时
总通知数: {total_notifications}
成功率: {success_rate}%
发送成功: {total_sent}
发送失败: {total_failed}
高峰时段: {peak_hour}:00"""
)
def generate_stats_report():
    return monitored_notify.get_stats()
```

### 2. 调试模式

```python
import os
from use_notify import useNotify, useNotifyChannel

class DebugNotify:
    """调试模式通知"""
    
    def __init__(self, debug=None):
        self.debug = debug if debug is not None else os.getenv('DEBUG', 'false').lower() == 'true'
        self.notify = self._create_notify()
    
    def _create_notify(self):
        """根据调试模式创建通知实例"""
        notify = useNotify()
        
        if self.debug:
            # 调试模式：使用控制台输出
            class DebugChannel:
                def send(self, title, content, **kwargs):
                    print(f"\n[DEBUG NOTIFICATION]")
                    print(f"Title: {title}")
                    print(f"Content: {content}")
                    print(f"Kwargs: {kwargs}")
                    print(f"Timestamp: {datetime.now()}")
                    print("-" * 50)
                    return True
                
                async def send_async(self, title, content, **kwargs):
                    return self.send(title, content, **kwargs)
            
            notify.add(DebugChannel())
        else:
            # 生产模式：使用实际通知渠道
            if os.getenv("BARK_TOKEN"):
                notify.add(useNotifyChannel.Bark({"token": os.getenv("BARK_TOKEN")}))
            
            if os.getenv("DING_TOKEN"):
                notify.add(useNotifyChannel.Ding({"token": os.getenv("DING_TOKEN")}))
        
        return notify
    
    def publish(self, title, content, **kwargs):
        """发送通知"""
        if self.debug:
            print(f"[DEBUG] 准备发送通知: {title}")
        
        return self.notify.publish(title=title, content=content, **kwargs)

# 使用调试通知
debug_notify = DebugNotify()

# 在装饰器中使用
from use_notify import set_default_notify_instance
set_default_notify_instance(debug_notify)

@notify(title="调试任务")
def debug_task():
    return "任务执行完成"
```

## 安全最佳实践

### 1. 敏感信息处理

```python
import re
from use_notify import notify

class SecureNotify:
    """安全的通知处理"""
    
    # 敏感信息模式
    SENSITIVE_PATTERNS = [
        r'password[\s]*[:=][\s]*[\S]+',
        r'token[\s]*[:=][\s]*[\S]+',
        r'key[\s]*[:=][\s]*[\S]+',
        r'secret[\s]*[:=][\s]*[\S]+',
        r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',  # 信用卡号
        r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
    ]
    
    @classmethod
    def sanitize_content(cls, content):
        """清理敏感信息"""
        sanitized = str(content)
        
        for pattern in cls.SENSITIVE_PATTERNS:
            sanitized = re.sub(pattern, '[REDACTED]', sanitized, flags=re.IGNORECASE)
        
        return sanitized
    
    @classmethod
    def safe_notify(cls, title, content, **kwargs):
        """安全的通知发送"""
        safe_title = cls.sanitize_content(title)
        safe_content = cls.sanitize_content(content)
        
        # 记录原始内容到安全日志（如果需要）
        logger.info(f"发送通知: {safe_title}")
        
        return notify.publish(title=safe_title, content=safe_content, **kwargs)

# ✅ 推荐：使用安全通知
@notify(
    title="用户操作日志",
    content_template=lambda result: SecureNotify.sanitize_content(
        f"用户 {result['user']} 执行了操作: {result['action']}"
    )
)
def log_user_action(user, action, details):
    return {
        'user': user,
        'action': action,
        'details': details,
        'timestamp': datetime.now().isoformat()
    }
```

### 2. 访问控制

```python
from functools import wraps
from use_notify import notify

def require_permission(permission):
    """权限检查装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 检查用户权限
            current_user = get_current_user()
            if not has_permission(current_user, permission):
                raise PermissionError(f"用户 {current_user} 没有 {permission} 权限")
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

# ✅ 推荐：结合权限控制使用通知
@require_permission('admin')
@notify(
    title="管理员操作",
    content_template="管理员 {user} 执行了 {operation}"
)
def admin_operation(operation):
    user = get_current_user()
    execute_admin_operation(operation)
    
    return {
        'user': user,
        'operation': operation,
        'timestamp': datetime.now().isoformat()
    }
```

## 测试策略

### 1. 单元测试

```python
import unittest
from unittest.mock import Mock, patch
from use_notify import useNotify, notify

class TestNotifications(unittest.TestCase):
    """通知功能测试"""
    
    def setUp(self):
        """测试设置"""
        self.mock_channel = Mock()
        self.mock_channel.send.return_value = True
        self.mock_channel.send_async.return_value = True
        
        self.notify = useNotify()
        self.notify.add(self.mock_channel)
    
    def test_basic_notification(self):
        """测试基本通知功能"""
        self.notify.publish(title="测试", content="测试内容")
        
        self.mock_channel.send.assert_called_once_with(
            title="测试",
            content="测试内容"
        )
    
    def test_decorator_notification(self):
        """测试装饰器通知"""
        @notify(
            notify_instance=self.notify,
            title="装饰器测试",
            content_template="结果: {result}"
        )
        def test_function():
            return "成功"
        
        result = test_function()
        
        self.assertEqual(result, "成功")
        self.mock_channel.send.assert_called_once()
        
        # 检查调用参数
        call_args = self.mock_channel.send.call_args
        self.assertEqual(call_args[1]['title'], "装饰器测试")
        self.assertIn("成功", call_args[1]['content'])
    
    def test_conditional_notification(self):
        """测试条件通知"""
        @notify(
            notify_instance=self.notify,
            condition=lambda result: result > 10,
            title="条件测试"
        )
        def conditional_function(value):
            return value
        
        # 不满足条件，不应该发送通知
        conditional_function(5)
        self.mock_channel.send.assert_not_called()
        
        # 满足条件，应该发送通知
        conditional_function(15)
        self.mock_channel.send.assert_called_once()
    
    @patch('use_notify.channels.requests.post')
    def test_channel_failure_handling(self, mock_post):
        """测试渠道失败处理"""
        # 模拟网络错误
        mock_post.side_effect = Exception("网络错误")
        
        with self.assertLogs() as log:
            try:
                self.notify.publish(title="测试", content="测试内容")
            except Exception:
                pass
        
        # 验证错误被正确记录
        self.assertTrue(any("网络错误" in record.message for record in log.records))

class TestNotificationIntegration(unittest.TestCase):
    """通知集成测试"""
    
    def test_end_to_end_workflow(self):
        """端到端工作流测试"""
        # 创建测试通知实例
        test_notify = useNotify()
        
        # 添加测试渠道
        test_channel = Mock()
        test_channel.send.return_value = True
        test_notify.add(test_channel)
        
        # 模拟完整的业务流程
        @notify(
            notify_instance=test_notify,
            title="业务流程完成",
            condition=lambda result: result['success'],
            content_template="处理了 {count} 项数据，耗时 {duration} 秒"
        )
        def business_process(data):
            start_time = time.time()
            
            # 模拟数据处理
            processed_count = len(data)
            time.sleep(0.1)  # 模拟处理时间
            
            duration = round(time.time() - start_time, 2)
            
            return {
                'success': True,
                'count': processed_count,
                'duration': duration
            }
        
        # 执行业务流程
        test_data = [1, 2, 3, 4, 5]
        result = business_process(test_data)
        
        # 验证结果
        self.assertTrue(result['success'])
        self.assertEqual(result['count'], 5)
        
        # 验证通知被发送
        test_channel.send.assert_called_once()
        
        # 验证通知内容
        call_args = test_channel.send.call_args
        self.assertEqual(call_args[1]['title'], "业务流程完成")
        self.assertIn("5", call_args[1]['content'])  # 包含处理数量

if __name__ == '__main__':
    unittest.main()
```

### 2. 性能测试

```python
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor
from use_notify import useNotify, notify

def performance_test():
    """性能测试"""
    
    # 创建测试通知实例
    test_notify = useNotify()
    
    # 添加快速测试渠道
    class FastTestChannel:
        def __init__(self):
            self.call_count = 0
        
        def send(self, title, content, **kwargs):
            self.call_count += 1
            time.sleep(0.001)  # 模拟1ms延迟
            return True
        
        async def send_async(self, title, content, **kwargs):
            self.call_count += 1
            await asyncio.sleep(0.001)  # 模拟1ms异步延迟
            return True
    
    test_channel = FastTestChannel()
    test_notify.add(test_channel)
    
    # 测试同步性能
    print("测试同步通知性能...")
    start_time = time.time()
    
    for i in range(100):
        test_notify.publish(title=f"测试 {i}", content=f"内容 {i}")
    
    sync_duration = time.time() - start_time
    print(f"同步发送100条通知耗时: {sync_duration:.2f}秒")
    print(f"平均每条通知耗时: {sync_duration/100*1000:.2f}ms")
    
    # 测试异步性能
    async def async_performance_test():
        print("\n测试异步通知性能...")
        start_time = time.time()
        
        tasks = []
        for i in range(100):
            task = test_notify.publish_async(title=f"异步测试 {i}", content=f"异步内容 {i}")
            tasks.append(task)
        
        await asyncio.gather(*tasks)
        
        async_duration = time.time() - start_time
        print(f"异步发送100条通知耗时: {async_duration:.2f}秒")
        print(f"平均每条通知耗时: {async_duration/100*1000:.2f}ms")
        print(f"性能提升: {sync_duration/async_duration:.2f}x")
    
    asyncio.run(async_performance_test())
    
    print(f"\n总调用次数: {test_channel.call_count}")

if __name__ == '__main__':
    performance_test()
```

通过遵循这些最佳实践，您可以构建一个可靠、高效、易维护的通知系统。记住要根据具体的业务需求和环境特点来调整这些实践，确保通知系统能够真正为您的应用程序增值。