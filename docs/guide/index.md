# use-notify 简介

use-notify 是一个用于 Python 的消息通知库，提供了简单而强大的 API 来集成多种消息通知渠道，支持同步和异步操作。

## 特性

- **多渠道支持**
  - 钉钉（DingTalk）
  - 企业微信（WeChat Work）
  - Bark（iOS 推送）
  - Pushover
  - Pushdeer
  - 邮件（Email）
  - Chanify
  - 飞书（Feishu）
  - Ntfy

- **装饰器模式**
  - 使用 `@notify` 装饰器自动化通知
  - 支持成功/失败通知
  - 自定义消息模板
  - 条件通知

- **高级特性**
  - 异步/同步双模式支持
  - 全局默认实例管理
  - 完整的类型提示
  - 高度可扩展的架构
  - 错误处理和重试机制

## 依赖要求

- Python 3.8+
- httpx
- usepy

## 安装

使用 pip 安装：

```bash
pip install use-notify
```

## 快速预览

### 基础使用

```python
from use_notify import useNotify, useNotifyChannel

# 创建通知实例
notify = useNotify()
notify.add(
    useNotifyChannel.Bark({"token": "your_bark_token"}),
    useNotifyChannel.Ding({"token": "your_ding_token"})
)

# 发送通知
notify.publish(title="消息标题", content="消息正文")
```

### 装饰器使用

```python
from use_notify import notify, set_default_notify_instance

# 设置全局默认实例
set_default_notify_instance(notify)

# 使用装饰器
@notify()
def my_task():
    # 您的业务逻辑
    return "任务完成"

# 执行函数，自动发送通知
result = my_task()
```
