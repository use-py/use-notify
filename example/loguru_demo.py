# -*- coding: utf-8 -*-
"""
Loguru日志上报示例

这个示例展示了如何使用use-notify库集成loguru实现日志上报功能
"""

from loguru import logger
from use_notify import useNotifyChannel, setup_loguru_reporter
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from use_notify.loguru_types import ExtendedLogger
    logger = logger  # type: ExtendedLogger


def example_basic_usage():
    """基础使用示例"""
    print("=== 基础使用示例 ===")
    
    # 方式1: 使用配置字典设置
    settings = {
        "BARK": {"token": "your_bark_token"},
        "WECHAT": {"token": "your_wechat_token"},
    }
    
    # 设置loguru上报器，ERROR级别及以上会触发上报
    reporter = setup_loguru_reporter(settings=settings, level="ERROR")
    
    # 现在可以使用logger.report()进行上报
    logger.report("这是一条需要上报的错误消息")
    
    # 也可以指定级别和额外信息
    logger.report(
        "系统出现异常", 
        level="CRITICAL",
        服务器="web-01",
        错误代码="E001"
    )
    
    print("基础示例完成")


def example_channel_instances():
    """使用通道实例的示例"""
    print("\n=== 使用通道实例示例 ===")
    
    # 方式2: 直接使用通道实例
    channels = [
        useNotifyChannel.Bark({"token": "your_bark_token"}),
        useNotifyChannel.WeChat({"token": "your_wechat_token"}),
    ]
    
    # 设置上报器
    reporter = setup_loguru_reporter(channels=channels, level="WARNING")
    
    # 测试上报
    logger.report("这是一条警告消息", level="WARNING")
    
    print("通道实例示例完成")


def example_manual_setup():
    """手动设置示例"""
    print("\n=== 手动设置示例 ===")
    
    from use_notify import LoguruReporter, useNotify
    
    # 创建通知实例
    notify = useNotify()
    notify.add(
        useNotifyChannel.Bark({"token": "your_bark_token"}),
        useNotifyChannel.WeChat({"token": "your_wechat_token"}),
    )
    
    # 创建上报器
    reporter = LoguruReporter(notify)
    
    # 配置logger
    reporter.configure_logger(level="INFO")
    
    # 测试上报
    logger.report("手动设置的上报消息", level="INFO", 模块="demo")
    
    print("手动设置示例完成")


def example_with_exception():
    """异常上报示例"""
    print("\n=== 异常上报示例 ===")
    
    # 设置上报器
    settings = {"BARK": {"token": "your_bark_token"}}
    setup_loguru_reporter(settings=settings, level="ERROR")
    
    try:
        # 模拟一个异常
        result = 1 / 0
    except Exception as e:
        # 上报异常信息
        logger.report(
            f"计算异常: {str(e)}", 
            level="ERROR",
            函数="example_with_exception",
            输入参数="1 / 0"
        )
    
    print("异常上报示例完成")


def example_different_levels():
    """不同级别上报示例"""
    print("\n=== 不同级别上报示例 ===")
    
    # 设置上报器，INFO级别及以上会触发上报
    settings = { "wecom": {
        "token": "8299d821-dbdd-44e5-b554-9c9a774f8cf9",
    }}
    setup_loguru_reporter(settings=settings, level="INFO")
    
    # 测试不同级别的上报
    logger.report("这是信息级别", level="INFO")
    logger.report("这是警告级别", level="WARNING")
    logger.report("这是错误级别", level="ERROR")
    logger.report("这是严重错误级别", level="CRITICAL")
    
    print("不同级别示例完成")


if __name__ == "__main__":
    print("Loguru日志上报功能演示")
    print("注意: 请先配置正确的token才能实际发送通知")
    
    # 运行示例（注释掉避免实际发送）
    # example_basic_usage()
    # example_channel_instances()
    # example_manual_setup()
    # example_with_exception()
    example_different_levels()
    
    print("\n所有示例代码已准备就绪，请配置token后取消注释运行")
