#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
演示如何在通知模板中使用当前时间变量 current_time
"""

import time

from use_notify import useNotify
from use_notify.channels.base import BaseChannel


# 创建一个模拟的通知渠道用于演示
class DemoChannel(BaseChannel):
    def __init__(self):
        super().__init__({})
    
    def send(self, content, title=None):
        print(f"📧 通知标题: {title}")
        print(f"📝 通知内容: {content}")
        print("-" * 50)
    
    async def send_async(self, content, title=None):
        self.send(content, title)


def main():
    # 创建通知实例
    demo_channel = DemoChannel()
    notify_instance = useNotify([demo_channel])
    
    # 使用包含当前时间的自定义模板
    success_template = (
        "✅ 函数 {function_name} 执行成功\n"
        "⏱️ 执行时间: {execution_time:.2f}秒\n"
        "🕐 开始时间: {start_time}\n"
        "🕐 结束时间: {end_time}\n"
        "🕐 通知时间: {current_time}"
    )
    
    error_template = (
        "❌ 函数 {function_name} 执行失败\n"
        "⏱️ 执行时间: {execution_time:.2f}秒\n"
        "🕐 开始时间: {start_time}\n"
        "🕐 结束时间: {end_time}\n"
        "🕐 通知时间: {current_time}\n"
        "🚨 错误信息: {error_message}"
    )
    
    # 使用装饰器和自定义模板
    from use_notify.decorator import notify
    
    @notify(
        notify_instance=notify_instance,
        success_template=success_template,
        error_template=error_template
    )
    def successful_task():
        """一个成功的任务"""
        print("正在执行任务...")
        time.sleep(1)  # 模拟任务执行
        return "任务完成"
    
    @notify(
        notify_instance=notify_instance,
        success_template=success_template,
        error_template=error_template
    )
    def failing_task():
        """一个失败的任务"""
        print("正在执行任务...")
        time.sleep(0.5)  # 模拟任务执行
        raise ValueError("模拟的错误")
    
    print("=== 演示成功任务通知 ===")
    try:
        result = successful_task()
        print(f"任务结果: {result}")
    except Exception as e:
        print(f"任务失败: {e}")
    
    print("\n=== 演示失败任务通知 ===")
    try:
        failing_task()
    except Exception as e:
        print(f"任务失败: {e}")
    
    print("\n=== 说明 ===")
    print("在上面的通知中，你可以看到:")
    print("- start_time: 函数开始执行的时间")
    print("- end_time: 函数结束执行的时间")
    print("- current_time: 发送通知时的当前时间")
    print("\n注意: current_time 通常会比 end_time 稍晚一些，")
    print("因为它是在格式化通知消息时获取的当前时间。")


if __name__ == "__main__":
    main()
