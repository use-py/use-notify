#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@notify 装饰器全局默认实例演示

本示例展示如何设置全局默认通知实例，
避免每次使用装饰器都需要传递 notify_instance 参数。
"""

import asyncio
import sys
import os
import time

from use_notify.channels.console import Console as ConsoleChannel

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from use_notify import (
    useNotify, 
    notify, 
    set_default_notify_instance,
    get_default_notify_instance,
    clear_default_notify_instance
)
from use_notify.channels.base import BaseChannel

def setup_default_notify_instance():
    """设置全局默认通知实例"""
    print("🔧 设置全局默认通知实例...")
    
    # 创建通知实例
    default_notify = useNotify()
    default_notify.add(ConsoleChannel())
    
    # 设置为全局默认实例
    set_default_notify_instance(default_notify)
    
    print("✅ 全局默认通知实例设置完成")
    return default_notify

setup_default_notify_instance()


# 现在可以直接使用装饰器，无需传递 notify_instance 参数
@notify()
def simple_task():
    """简单任务 - 使用默认实例"""
    time.sleep(1)
    return "简单任务完成"


@notify(title="数据处理任务")
def process_data(count):
    """数据处理任务 - 使用默认实例和自定义标题"""
    print(f"正在处理 {count} 条数据...")
    time.sleep(1.5)
    return f"成功处理 {count} 条数据"


@notify(
    title="高级任务",
    success_template="🎯 {function_name} 完成\n📊 参数: {args}\n⏱️ 耗时: {execution_time:.2f}秒\n📋 结果: {result}",
    include_args=True,
    include_result=True
)
def advanced_task(task_type, priority="normal"):
    """高级任务 - 使用默认实例和自定义模板"""
    print(f"执行 {task_type} 任务，优先级: {priority}")
    time.sleep(2)
    return {"status": "completed", "task_type": task_type, "priority": priority}


@notify(
    notify_on_success=False,  # 只在失败时通知
    error_template="🚨 监控告警\n🖥️ 服务: {args[0]}\n❗ 错误: {error_message}"
)
def health_check(service_name):
    """健康检查 - 只在失败时使用默认实例通知"""
    print(f"检查服务: {service_name}")
    time.sleep(0.5)
    
    # 模拟随机失败
    import random
    if random.random() < 0.3:  # 30% 失败率
        raise RuntimeError(f"{service_name} 服务异常")
    
    return f"{service_name} 服务正常"


@notify(title="异步任务")
async def async_download(url):
    """异步下载任务 - 使用默认实例"""
    print(f"开始下载: {url}")
    await asyncio.sleep(2)
    return f"下载完成: {url}"


# 演示覆盖默认实例
def demo_override_instance():
    """演示如何在特定装饰器中覆盖默认实例"""
    print("\n=== 覆盖默认实例演示 ===")
    
    # 创建另一个通知实例
    class SpecialChannel(BaseChannel):
        def __init__(self, config=None):
            super().__init__(config or {})
        
        def send(self, title, content):
            print(f"\n🔥 [特殊通知] {title}")
            print(f"🔥 {content}")
            print("=" * 50)
        
        async def send_async(self, title, content):
            print(f"\n🔥 [特殊异步通知] {title}")
            print(f"🔥 {content}")
            print("=" * 50)
    
    special_notify = useNotify()
    special_notify.add(SpecialChannel())
    
    # 使用特定的通知实例（覆盖默认实例）
    @notify(
        notify_instance=special_notify,
        title="特殊任务",
        success_template="🌟 特殊任务 {function_name} 完成"
    )
    def special_task():
        time.sleep(1)
        return "特殊任务完成"
    
    print("执行特殊任务（使用特定通知实例）...")
    result = special_task()
    print(f"结果: {result}")


def main():
    """主函数"""
    print("🚀 @notify 装饰器全局默认实例演示")
    print("=" * 60)
    
    print(f"\n📋 当前默认实例: {get_default_notify_instance()}")
    
    # 2. 使用默认实例的基础示例
    print("\n=== 基础使用（无需传递 notify_instance）===")
    print("执行简单任务...")
    result = simple_task()
    print(f"结果: {result}")
    
    # 3. 使用默认实例的自定义配置
    print("\n=== 自定义配置（使用默认实例）===")
    print("执行数据处理任务...")
    result = process_data(1000)
    print(f"结果: {result}")
    
    # 4. 高级配置示例
    print("\n=== 高级配置（使用默认实例）===")
    print("执行高级任务...")
    result = advanced_task("数据分析", priority="high")
    print(f"结果: {result}")
    
    # 5. 健康检查示例（多次执行以演示失败通知）
    print("\n=== 健康检查（只在失败时通知）===")
    services = ["数据库", "Redis", "API网关", "消息队列", "文件存储"]
    for service in services:
        try:
            result = health_check(service)
            print(f"✅ {result}")
        except Exception as e:
            print(f"❌ {service} 检查失败: {e}")
    
    # 6. 覆盖默认实例演示
    demo_override_instance()
    
    print("\n=== 清除默认实例演示 ===")
    clear_default_notify_instance()
    print(f"清除后的默认实例: {get_default_notify_instance()}")
    
    # 7. 清除后使用装饰器（会创建空实例并警告）
    @notify(title="清除后的任务")
    def task_after_clear():
        return "任务完成"
    
    print("\n执行清除默认实例后的任务...")
    result = task_after_clear()
    print(f"结果: {result}")


async def async_main():
    """异步示例"""
    print("\n=== 异步任务（使用默认实例）===")
    
    # 重新设置默认实例（因为之前被清除了）
    setup_default_notify_instance()
    
    print("执行异步下载任务...")
    result = await async_download("https://example.com/file.zip")
    print(f"结果: {result}")


if __name__ == "__main__":
    # 执行同步示例
    main()
    
    # 执行异步示例
    asyncio.run(async_main())
    
    print("\n" + "=" * 60)
    print("🎉 演示完成！")
    print("\n💡 使用提示:")
    print("1. 使用 set_default_notify_instance() 设置全局默认通知实例")
    print("2. 设置后，所有 @notify() 装饰器都会自动使用默认实例")
    print("3. 仍可通过 notify_instance 参数覆盖默认实例")
    print("4. 使用 clear_default_notify_instance() 清除默认实例")
    print("5. 使用 get_default_notify_instance() 获取当前默认实例")
