#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@notify 装饰器真实使用示例

本示例展示如何在实际项目中使用 @notify 装饰器，
包括与真实通知渠道的集成。
"""

import asyncio
import sys
import os
import time
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from use_notify import useNotify, useNotifyChannel, notify


def create_notify_instance():
    """创建通知实例"""
    # 方式1: 使用配置字典
    settings = {
        # "BARK": {"token": "your_bark_token_here"},
        # "DINGTALK": {"access_token": "your_dingtalk_token_here"},
        # "WECHAT": {"token": "your_wechat_webhook_token_here"},
    }
    
    # 如果有配置，使用 from_settings 创建
    if settings:
        return useNotify.from_settings(settings)
    
    # 方式2: 手动添加通道
    notify_instance = useNotify()
    # notify_instance.add(
    #     useNotifyChannel.Bark({"token": "your_bark_token_here"}),
    #     useNotifyChannel.DingTalk({"access_token": "your_dingtalk_token_here"})
    # )
    
    return notify_instance


# 创建全局通知实例
notify_instance = create_notify_instance()


# 示例1: 数据处理任务
@notify(
    notify_instance=notify_instance,
    title="数据处理任务",
    success_template="✅ {function_name} 处理完成\n📊 处理了 {args[0]} 条记录\n⏱️ 耗时: {execution_time:.2f}秒",
    error_template="❌ {function_name} 处理失败\n📊 目标记录: {args[0]} 条\n⏱️ 耗时: {execution_time:.2f}秒\n🚨 错误: {error_message}",
    include_args=True
)
def process_user_data(record_count):
    """处理用户数据"""
    print(f"开始处理 {record_count} 条用户数据...")
    
    # 模拟数据处理
    for i in range(record_count // 100):
        time.sleep(0.1)  # 模拟处理时间
        print(f"已处理 {(i + 1) * 100} 条记录")
    
    # 模拟可能的错误
    if record_count > 10000:
        raise ValueError("记录数量超过系统限制")
    
    return f"成功处理 {record_count} 条用户数据"


# 示例2: 文件备份任务
@notify(
    notify_instance=notify_instance,
    title="文件备份",
    success_template="💾 备份完成\n📁 源路径: {args[0]}\n📁 目标路径: {args[1]}\n⏱️ 耗时: {execution_time:.2f}秒\n📋 结果: {result}",
    include_args=True,
    include_result=True
)
def backup_files(source_path, target_path):
    """备份文件"""
    print(f"开始备份: {source_path} -> {target_path}")
    
    # 模拟备份过程
    time.sleep(2)
    
    return {
        "files_copied": 150,
        "total_size": "2.3GB",
        "backup_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


# 示例3: 异步API调用
@notify(
    notify_instance=notify_instance,
    title="API数据同步",
    success_template="🔄 API同步完成\n🌐 接口: {kwargs[api_endpoint]}\n📊 同步数据: {result[records_synced]} 条\n⏱️ 耗时: {execution_time:.2f}秒",
    error_template="🔄 API同步失败\n🌐 接口: {kwargs[api_endpoint]}\n⏱️ 耗时: {execution_time:.2f}秒\n🚨 错误: {error_message}",
    include_args=True,
    include_result=True
)
async def sync_api_data(api_endpoint, batch_size=100):
    """异步同步API数据"""
    print(f"开始同步API数据: {api_endpoint}")
    
    # 模拟API调用
    await asyncio.sleep(3)
    
    return {
        "records_synced": 500,
        "last_sync_time": datetime.now().isoformat(),
        "status": "success"
    }


# 示例4: 监控任务（只在失败时通知）
@notify(
    notify_instance=notify_instance,
    title="系统监控",
    notify_on_success=False,  # 不发送成功通知
    notify_on_error=True,     # 只发送失败通知
    error_template="🚨 系统监控告警\n🖥️ 检查项: {args[0]}\n⏱️ 检查时间: {execution_time:.2f}秒\n❗ 错误详情: {error_message}"
)
def health_check(check_name):
    """系统健康检查"""
    print(f"执行健康检查: {check_name}")
    
    # 模拟检查过程
    time.sleep(0.5)
    
    # 模拟检查结果
    import random
    if random.random() < 0.1:  # 10% 概率失败
        raise RuntimeError(f"{check_name} 检查失败: 响应超时")
    
    return f"{check_name} 检查通过"


# 示例5: 批量任务处理
@notify(
    notify_instance=notify_instance,
    title="批量任务",
    success_template=(
        "🎯 批量任务完成\n"
        "📋 任务类型: {kwargs[task_type]}\n"
        "📊 处理数量: {args[0]} 个\n"
        "✅ 成功: {result[success_count]} 个\n"
        "❌ 失败: {result[failed_count]} 个\n"
        "⏱️ 总耗时: {execution_time:.2f}秒"
    ),
    include_args=True,
    include_result=True
)
def batch_process_tasks(task_count, task_type="default", parallel=False):
    """批量处理任务"""
    print(f"开始批量处理 {task_count} 个 {task_type} 任务")
    
    success_count = 0
    failed_count = 0
    
    for i in range(task_count):
        time.sleep(0.1)  # 模拟任务处理
        
        # 模拟成功/失败
        import random
        if random.random() < 0.9:  # 90% 成功率
            success_count += 1
        else:
            failed_count += 1
        
        if (i + 1) % 10 == 0:
            print(f"已处理 {i + 1}/{task_count} 个任务")
    
    return {
        "success_count": success_count,
        "failed_count": failed_count,
        "total_count": task_count
    }


def main():
    """主函数 - 同步示例"""
    print("🚀 @notify 装饰器真实使用示例")
    print("=" * 50)
    
    # 示例1: 数据处理
    print("\n1. 执行数据处理任务...")
    try:
        result = process_user_data(1000)
        print(f"✅ {result}")
    except Exception as e:
        print(f"❌ 处理失败: {e}")
    
    # 示例2: 文件备份
    print("\n2. 执行文件备份任务...")
    try:
        result = backup_files("/data/source", "/backup/target")
        print(f"✅ 备份完成: {result}")
    except Exception as e:
        print(f"❌ 备份失败: {e}")
    
    # 示例3: 健康检查（多次执行以演示失败通知）
    print("\n3. 执行系统健康检查...")
    for check in ["数据库连接", "Redis连接", "API服务", "磁盘空间", "内存使用"]:
        try:
            result = health_check(check)
            print(f"✅ {result}")
        except Exception as e:
            print(f"❌ {check} 失败: {e}")
    
    # 示例4: 批量任务
    print("\n4. 执行批量任务处理...")
    try:
        result = batch_process_tasks(50, task_type="数据清理", parallel=True)
        print(f"✅ 批量任务完成: {result}")
    except Exception as e:
        print(f"❌ 批量任务失败: {e}")


async def async_main():
    """异步主函数"""
    print("\n5. 执行异步API同步...")
    try:
        result = await sync_api_data(
            api_endpoint="https://api.example.com/users",
            batch_size=200
        )
        print(f"✅ API同步完成: {result}")
    except Exception as e:
        print(f"❌ API同步失败: {e}")


if __name__ == "__main__":
    # 执行同步示例
    main()
    
    # 执行异步示例
    asyncio.run(async_main())
    
    print("\n" + "=" * 50)
    print("🎉 示例执行完成！")
    print("\n💡 配置提示:")
    print("1. 请在 create_notify_instance() 函数中配置真实的通知渠道")
    print("2. 取消注释相应的通知渠道配置代码")
    print("3. 替换为您的真实 token 或 access_token")
    print("4. 支持的通知渠道: Bark, DingTalk, WeChat, Email, PushDeer 等")
