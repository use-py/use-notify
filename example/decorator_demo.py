#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@notify 装饰器功能演示

本演示展示了 @notify 装饰器的各种使用方式，包括：
1. 基础使用
2. 自定义配置
3. 异步函数支持
4. 错误处理
5. 高级配置选项
"""

import asyncio
import sys
import os
import time
from datetime import datetime

from use_notify.channels.wechat import WeChat

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from use_notify import useNotify, useNotifyChannel, notify
from use_notify.channels.base import BaseChannel


# 创建一个模拟通知渠道用于演示
class ConsoleChannel(BaseChannel):
    """控制台输出通知渠道（用于演示）"""
    
    def __init__(self, config=None):
        super().__init__(config or {})
    
    def send(self, title=None, content=None, **kwargs):
        print(f"\n📢 [同步通知] {title}")
        print(f"📝 {content}")
        print("-" * 50)
    
    async def send_async(self, title=None, content=None, **kwargs):
        print(f"\n📢 [异步通知] {title}")
        print(f"📝 {content}")
        print("-" * 50)


def demo_basic_usage():
    """演示基础使用"""
    print("\n=== 基础使用演示 ===")
    
    # 创建通知实例
    notify_instance = useNotify([ConsoleChannel()])
    
    # 基础装饰器使用
    @notify(notify_instance=notify_instance)
    def simple_task():
        """简单任务"""
        time.sleep(1)  # 模拟任务执行
        return "任务完成"
    
    print("执行简单任务...")
    result = simple_task()
    print(f"任务结果: {result}")


def demo_custom_configuration():
    """演示自定义配置"""
    print("\n=== 自定义配置演示 ===")
    
    notify_instance = useNotify([ConsoleChannel()])
    
    # 自定义标题和模板
    @notify(
        notify_instance=notify_instance,
        title="重要数据处理任务",
        success_template="✅ {function_name} 成功处理了 {args[0]} 条记录，耗时 {execution_time:.2f}秒",
        error_template="❌ {function_name} 处理失败: {error_message}，已处理时间 {execution_time:.2f}秒",
        include_args=True,
        include_result=True
    )
    def process_data(record_count):
        """数据处理任务"""
        print(f"正在处理 {record_count} 条记录...")
        time.sleep(1.5)  # 模拟处理时间
        return f"成功处理了 {record_count} 条记录"
    
    print("执行数据处理任务...")
    result = process_data(1000)
    print(f"处理结果: {result}")


async def demo_async_functions():
    """演示异步函数支持"""
    print("\n=== 异步函数演示 ===")
    
    notify_instance = useNotify([ConsoleChannel()])
    
    @notify(
        notify_instance=notify_instance,
        title="异步下载任务",
        success_template="📥 {function_name} 下载完成，文件大小: {result}，耗时 {execution_time:.2f}秒",
        include_result=True
    )
    async def download_file(url):
        """异步下载文件"""
        print(f"开始下载: {url}")
        await asyncio.sleep(2)  # 模拟下载时间
        return "1.5MB"
    
    print("执行异步下载任务...")
    result = await download_file("https://example.com/file.zip")
    print(f"下载结果: {result}")


def demo_error_handling():
    """演示错误处理"""
    print("\n=== 错误处理演示 ===")
    
    notify_instance = useNotify([ConsoleChannel()])
    
    @notify(
        notify_instance=notify_instance,
        title="可能失败的任务",
        error_template="💥 {function_name} 执行失败\n🕐 执行时间: {execution_time:.2f}秒\n❗ 错误详情: {error_message}"
    )
    def risky_task(should_fail=False):
        """可能失败的任务"""
        time.sleep(0.5)
        if should_fail:
            raise ValueError("模拟的业务逻辑错误")
        return "任务成功完成"
    
    # 成功情况
    print("执行成功的任务...")
    try:
        result = risky_task(should_fail=False)
        print(f"任务结果: {result}")
    except Exception as e:
        print(f"任务异常: {e}")
    
    # 失败情况
    print("\n执行失败的任务...")
    try:
        result = risky_task(should_fail=True)
        print(f"任务结果: {result}")
    except Exception as e:
        print(f"任务异常: {e}")


def demo_advanced_options():
    """演示高级配置选项"""
    print("\n=== 高级配置选项演示 ===")
    
    notify_instance = useNotify([ConsoleChannel()])
    
    # 只在失败时通知
    @notify(
        notify_instance=notify_instance,
        title="监控任务",
        notify_on_success=False,  # 不发送成功通知
        notify_on_error=True,     # 只发送失败通知
        timeout=5.0               # 5秒超时
    )
    def monitoring_task(check_status):
        """监控任务（只在失败时通知）"""
        time.sleep(0.3)
        if check_status == "error":
            raise RuntimeError("系统检测到异常状态")
        return "系统状态正常"
    
    # 成功情况（不会发送通知）
    print("执行正常监控检查...")
    try:
        result = monitoring_task("ok")
        print(f"监控结果: {result}")
        print("（注意：成功时不发送通知）")
    except Exception as e:
        print(f"监控异常: {e}")
    
    # 失败情况（会发送通知）
    print("\n执行异常监控检查...")
    try:
        result = monitoring_task("error")
        print(f"监控结果: {result}")
    except Exception as e:
        print(f"监控异常: {e}")


def demo_without_notify_instance():
    """演示不提供通知实例的情况"""
    print("\n=== 无通知实例演示 ===")
    
    # 不提供 notify_instance（会创建空实例，不会实际发送通知）
    @notify(title="测试任务")
    def test_task():
        """测试任务"""
        time.sleep(0.5)
        return "测试完成"
    
    print("执行测试任务（无通知渠道）...")
    result = test_task()
    print(f"任务结果: {result}")
    print("（注意：由于没有配置通知渠道，不会发送实际通知）")


def demo_complex_scenario():
    """演示复杂使用场景"""
    print("\n=== 复杂场景演示 ===")
    
    notify_instance = useNotify([ConsoleChannel()])
    
    @notify(
        notify_instance=notify_instance,
        title="批量处理任务",
        success_template=(
            "🎉 {function_name} 批量处理完成\n"
            "📊 处理统计:\n"
            "  - 输入文件: {args[0]}\n"
            "  - 处理模式: {kwargs[mode]}\n"
            "  - 执行时间: {execution_time:.2f}秒\n"
            "  - 处理结果: {result}"
        ),
        error_template=(
            "💥 {function_name} 批量处理失败\n"
            "📊 失败信息:\n"
            "  - 输入文件: {args[0]}\n"
            "  - 处理模式: {kwargs[mode]}\n"
            "  - 执行时间: {execution_time:.2f}秒\n"
            "  - 错误信息: {error_message}"
        ),
        include_args=True,
        include_result=True
    )
    def batch_process(input_file, output_file, mode="standard", validate=True):
        """批量处理任务"""
        print(f"开始批量处理: {input_file} -> {output_file}")
        print(f"处理模式: {mode}, 验证: {validate}")
        
        # 模拟处理过程
        time.sleep(2)
        
        if mode == "error":
            raise ValueError("处理模式配置错误")
        
        return {
            "processed_records": 5000,
            "success_rate": "99.8%",
            "output_size": "2.3MB"
        }
    
    print("执行复杂批量处理任务...")
    try:
        result = batch_process(
            "data/input.csv",
            "data/output.csv",
            mode="advanced",
            validate=True
        )
        print(f"处理结果: {result}")
    except Exception as e:
        print(f"处理异常: {e}")


async def main():
    """主函数"""
    print("🚀 @notify 装饰器功能演示")
    print("=" * 60)
    
    # 同步演示
    demo_basic_usage()
    demo_custom_configuration()
    demo_error_handling()
    demo_advanced_options()
    demo_without_notify_instance()
    demo_complex_scenario()
    
    # 异步演示
    await demo_async_functions()
    
    print("\n" + "=" * 60)
    print("🎉 演示完成！")
    print("\n💡 使用提示:")
    print("1. 在实际使用中，请配置真实的通知渠道（如 Bark、钉钉等）")
    print("2. 可以根据需要自定义消息模板和配置选项")
    print("3. 装饰器支持同步和异步函数")
    print("4. 通知发送失败不会影响原函数的执行")
    print("5. 可以通过配置选择只在成功或失败时发送通知")


if __name__ == "__main__":
    asyncio.run(main())
