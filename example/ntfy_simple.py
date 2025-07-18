# -*- coding: utf-8 -*-
"""
Ntfy.sh 通知渠道简单使用示例
"""

import asyncio
from use_notify.channels import Ntfy

# 基础使用
ntfy = Ntfy({"topic": "my-notifications"})

# 同步发送
try:
    ntfy.send("这是一条测试消息", "测试标题")
    print("✓ 同步消息发送成功")
except Exception as e:
    print(f"✗ 同步发送失败: {e}")


# 异步发送
async def async_example():
    await ntfy.send_async("这是异步消息", "异步标题")
    try:
        print("✓ 异步消息发送成功")
    except Exception as e:
        print(f"✗ 异步发送失败: {e}")


# 运行异步示例
asyncio.run(async_example())

# 高级功能示例
advanced_ntfy = Ntfy(
    {
        "topic": "my-notifications",
        "priority": 4,
        "tags": ["urgent", "demo"],
        "click": "https://example.com",
    }
)

try:
    advanced_ntfy.send("高优先级消息", "重要通知")
    print("✓ 高级功能消息发送成功")
except Exception as e:
    print(f"✗ 高级功能发送失败: {e}")
