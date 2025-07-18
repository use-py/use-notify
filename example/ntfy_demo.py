# -*- coding: utf-8 -*-
"""
Ntfy.sh 通知渠道使用示例

本示例展示了如何使用 ntfy.sh 通知渠道发送通知，包括：
1. 基础配置和使用
2. 高级功能配置
3. 同步和异步发送
4. 与其他渠道的组合使用
"""
import asyncio

from use_notify import useNotify
from use_notify.channels import Ntfy


def basic_usage_example():
    """基础使用示例"""
    print("=== 基础使用示例 ===")
    
    # 最简配置，只需要指定主题
    ntfy = Ntfy({
        "topic": "my-notifications"
    })
    
    # 发送简单消息
    try:
        ntfy.send("这是一条测试消息")
        print("✓ 基础消息发送成功")
    except Exception as e:
        print(f"✗ 发送失败: {e}")
    
    # 发送带标题的消息
    try:
        ntfy.send("这是消息内容", "消息标题")
        print("✓ 带标题消息发送成功")
    except Exception as e:
        print(f"✗ 发送失败: {e}")


def advanced_features_example():
    """高级功能使用示例"""
    print("\n=== 高级功能使用示例 ===")
    
    # 配置高级功能
    ntfy = Ntfy({
        "topic": "my-notifications",
        "priority": 4,  # 高优先级 (1-5)
        "tags": ["warning", "computer"],  # 标签
        "click": "https://example.com",  # 点击跳转链接
        "attach": "https://example.com/image.jpg"  # 附件
    })
    
    try:
        ntfy.send("这是一条高优先级警告消息", "系统警告")
        print("✓ 高级功能消息发送成功")
    except Exception as e:
        print(f"✗ 发送失败: {e}")


def custom_server_example():
    """自定义服务器示例"""
    print("\n=== 自定义服务器示例 ===")
    
    # 使用自托管的 ntfy.sh 服务器
    ntfy = Ntfy({
        "topic": "my-notifications",
        "base_url": "https://ntfy.example.com"  # 自定义服务器
    })
    
    try:
        ntfy.send("来自自定义服务器的消息", "自定义服务器")
        print("✓ 自定义服务器消息发送成功")
    except Exception as e:
        print(f"✗ 发送失败: {e}")


async def async_usage_example():
    """异步使用示例"""
    print("\n=== 异步使用示例 ===")
    
    ntfy = Ntfy({
        "topic": "my-notifications",
        "priority": 3
    })
    
    try:
        await ntfy.send_async("这是异步发送的消息", "异步消息")
        print("✓ 异步消息发送成功")
    except Exception as e:
        print(f"✗ 异步发送失败: {e}")


def publisher_integration_example():
    """与 Publisher 集成使用示例"""
    print("\n=== Publisher 集成示例 ===")
    
    # 创建通知发布器
    notify = useNotify()
    
    # 添加 ntfy 渠道
    notify.add(
        Ntfy({
            "topic": "my-notifications",
            "priority": 3,
            "tags": ["app", "notification"]
        })
    )
    
    try:
        notify.publish("通过 Publisher 发送的消息", "Publisher 消息")
        print("✓ Publisher 集成消息发送成功")
    except Exception as e:
        print(f"✗ Publisher 发送失败: {e}")


async def async_publisher_example():
    """异步 Publisher 示例"""
    print("\n=== 异步 Publisher 示例 ===")
    
    notify = useNotify()
    notify.add(
        Ntfy({
            "topic": "my-notifications",
            "priority": 2
        })
    )
    
    try:
        await notify.publish_async("异步 Publisher 消息", "异步 Publisher")
        print("✓ 异步 Publisher 消息发送成功")
    except Exception as e:
        print(f"✗ 异步 Publisher 发送失败: {e}")


def from_settings_example():
    """从配置创建示例"""
    print("\n=== 从配置创建示例 ===")
    
    # 配置字典
    settings = {
        "NTFY": {
            "topic": "my-notifications",
            "priority": 3,
            "tags": ["config", "demo"],
            "click": "https://github.com/ntfy-sh/ntfy"
        }
    }
    
    # 从配置创建通知器
    notify = useNotify.from_settings(settings)
    
    try:
        notify.publish("从配置创建的消息", "配置消息")
        print("✓ 从配置创建消息发送成功")
    except Exception as e:
        print(f"✗ 从配置发送失败: {e}")


def actions_example():
    """交互操作示例"""
    print("\n=== 交互操作示例 ===")
    
    # 配置交互操作
    ntfy = Ntfy({
        "topic": "my-notifications",
        "actions": [
            {
                "action": "view",
                "label": "打开网站",
                "url": "https://ntfy.sh"
            },
            {
                "action": "http",
                "label": "重启服务",
                "url": "https://api.example.com/restart",
                "method": "POST"
            }
        ]
    })
    
    try:
        ntfy.send("服务器需要重启，请选择操作", "服务器警告")
        print("✓ 交互操作消息发送成功")
    except Exception as e:
        print(f"✗ 交互操作发送失败: {e}")


async def main():
    """主函数，运行所有示例"""
    print("Ntfy.sh 通知渠道使用示例")
    print("=" * 50)
    
    # 同步示例
    basic_usage_example()
    advanced_features_example()
    custom_server_example()
    publisher_integration_example()
    from_settings_example()
    actions_example()
    
    # 异步示例
    await async_usage_example()
    await async_publisher_example()
    
    print("\n" + "=" * 50)
    print("所有示例运行完成！")
    print("\n注意：")
    print("1. 请将 'my-notifications' 替换为您的实际主题名称")
    print("2. 确保您的设备已订阅相应的主题")
    print("3. 如果使用自定义服务器，请确保服务器地址正确")


if __name__ == "__main__":
    # 运行示例
    asyncio.run(main())