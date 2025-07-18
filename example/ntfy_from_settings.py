# -*- coding: utf-8 -*-
"""
使用配置字典创建 Ntfy 通知渠道的简单示例
"""
from use_notify import useNotify

# 基础配置
settings = {
    "NTFY": {
        "topic": "my-notifications"
    }
}

# 从配置创建通知器
notify = useNotify.from_settings(settings)

# 发送通知
try:
    notify.publish("这是一条测试消息", "测试标题")
    print("✓ 消息发送成功")
except Exception as e:
    print(f"✗ 发送失败: {e}")


# 高级配置示例
advanced_settings = {
    "NTFY": {
        "topic": "my-notifications",
        "base_url": "https://ntfy.sh",  # 可选：自定义服务器
        "priority": 3,                   # 可选：优先级 (1-5)
        "tags": ["python", "demo"],     # 可选：标签
        "click": "https://github.com/ntfy-sh/ntfy",  # 可选：点击链接
        "actions": [                     # 可选：交互操作
            {
                "action": "view",
                "label": "查看详情",
                "url": "https://example.com"
            }
        ]
    }
}

# 使用高级配置
advanced_notify = useNotify.from_settings(advanced_settings)

try:
    advanced_notify.publish("这是一条高级配置的消息", "高级消息")
    print("✓ 高级消息发送成功")
except Exception as e:
    print(f"✗ 高级消息发送失败: {e}")