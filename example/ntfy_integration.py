# -*- coding: utf-8 -*-
"""
Ntfy.sh 与 useNotify 集成使用示例
"""
import asyncio
from use_notify import useNotify
from use_notify.channels import Ntfy

# 方式1: 直接添加 Ntfy 渠道
notify = useNotify()
notify.add(
    Ntfy({
        "topic": "my-notifications",
        "priority": 3,
        "tags": ["app", "notification"]
    })
)

# 同步发送
try:
    notify.publish("集成测试消息", "集成测试")
    print("✓ 集成同步发送成功")
except Exception as e:
    print(f"✗ 集成同步发送失败: {e}")

# 异步发送
async def async_integration():
    try:
        await notify.publish_async("异步集成消息", "异步集成")
        print("✓ 集成异步发送成功")
    except Exception as e:
        print(f"✗ 集成异步发送失败: {e}")

asyncio.run(async_integration())

# 方式2: 从配置创建
settings = {
    "NTFY": {
        "topic": "my-notifications",
        "priority": 4,
        "tags": ["config", "demo"],
        "click": "https://ntfy.sh"
    }
}

config_notify = useNotify.from_settings(settings)

try:
    config_notify.publish("配置创建的消息", "配置测试")
    print("✓ 配置方式发送成功")
except Exception as e:
    print(f"✗ 配置方式发送失败: {e}")