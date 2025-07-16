#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基础loguru集成功能验证脚本

这个脚本用于验证loguru集成功能是否正常工作
"""

import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from loguru import logger
from use_notify import setup_loguru_reporter, LoguruReporter, useNotifyChannel


def test_basic_functionality():
    """测试基础功能"""
    print("=== 测试基础功能 ===")
    
    try:
        # 创建一个mock通道用于测试
        class MockChannel:
            def __init__(self, config):
                self.config = config
                self.sent_messages = []
            
            def send(self, content, title=None):
                self.sent_messages.append({"title": title, "content": content})
                print(f"Mock发送通知: {title}")
                print(f"内容: {content[:100]}...")
            
            async def send_async(self, content, title=None):
                self.send(content, title)
        
        # 设置上报器
        mock_channel = MockChannel({"token": "test"})
        reporter = setup_loguru_reporter(channels=[mock_channel], level="INFO")
        
        print("✓ 上报器设置成功")
        
        # 测试report方法是否存在
        assert hasattr(logger, 'report'), "logger.report方法不存在"
        print("✓ logger.report方法已添加")
        
        # 测试上报功能
        logger.report("这是一条测试消息", level="INFO", 测试参数="test_value")
        print("✓ 上报功能调用成功")
        
        # 检查消息是否被发送
        assert len(mock_channel.sent_messages) > 0, "没有消息被发送"
        print(f"✓ 消息已发送，共{len(mock_channel.sent_messages)}条")
        
        # 检查消息内容
        message = mock_channel.sent_messages[0]
        assert "INFO" in message["title"], "标题中应包含日志级别"
        assert "这是一条测试消息" in message["content"], "内容中应包含原始消息"
        assert "测试参数" in message["content"], "内容中应包含额外参数"
        print("✓ 消息内容验证通过")
        
        return True
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_different_levels():
    """测试不同日志级别"""
    print("\n=== 测试不同日志级别 ===")
    
    try:
        class MockChannel:
            def __init__(self, config):
                self.config = config
                self.sent_messages = []
            
            def send(self, content, title=None):
                self.sent_messages.append({"title": title, "content": content})
            
            async def send_async(self, content, title=None):
                self.send(content, title)
        
        mock_channel = MockChannel({"token": "test"})
        reporter = setup_loguru_reporter(channels=[mock_channel], level="WARNING")
        
        # 测试不同级别
        logger.report("INFO消息", level="INFO")  # 应该不会发送
        logger.report("WARNING消息", level="WARNING")  # 应该发送
        logger.report("ERROR消息", level="ERROR")  # 应该发送
        
        # WARNING级别设置，应该只发送WARNING和ERROR
        expected_count = 2
        actual_count = len(mock_channel.sent_messages)
        
        print(f"预期消息数: {expected_count}, 实际消息数: {actual_count}")
        
        if actual_count == expected_count:
            print("✓ 日志级别过滤正常")
            return True
        else:
            print("✗ 日志级别过滤异常")
            return False
            
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False


def test_manual_setup():
    """测试手动设置"""
    print("\n=== 测试手动设置 ===")
    
    try:
        from use_notify import useNotify
        
        class MockChannel:
            def __init__(self, config):
                self.config = config
                self.sent_messages = []
            
            def send(self, content, title=None):
                self.sent_messages.append({"title": title, "content": content})
            
            async def send_async(self, content, title=None):
                self.send(content, title)
        
        # 手动创建notify实例
        notify = useNotify()
        mock_channel = MockChannel({"token": "test"})
        notify.add(mock_channel)
        
        # 创建reporter
        reporter = LoguruReporter(notify)
        reporter.configure_logger(level="ERROR")
        
        # 测试上报
        logger.report("手动设置测试", level="ERROR")
        
        assert len(mock_channel.sent_messages) > 0, "手动设置的上报器没有工作"
        print("✓ 手动设置功能正常")
        
        return True
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("开始验证loguru集成功能...\n")
    
    tests = [
        test_basic_functionality,
        test_different_levels,
        test_manual_setup,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n=== 测试结果 ===")
    print(f"通过: {passed}/{total}")
    
    if passed == total:
        print("🎉 所有测试通过！loguru集成功能正常工作")
        return True
    else:
        print("❌ 部分测试失败，请检查实现")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)