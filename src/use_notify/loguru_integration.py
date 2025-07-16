# -*- coding: utf-8 -*-
import sys
from typing import Dict, Any, Optional, List
from loguru import logger
from .notification import Notify
from . import channels as channels_models


class LoguruReporter:
    """Loguru日志上报器，支持通过logger.report()进行消息通知"""
    
    def __init__(self, notify_instance: Optional[Notify] = None):
        self.notify = notify_instance or Notify()
        self._is_configured = False
    
    def add_channel(self, *channels):
        """添加通知渠道"""
        self.notify.add(*channels)
    
    def configure_logger(self, level: str = "ERROR", format_string: Optional[str] = None):
        """配置loguru logger，添加上报功能
        
        Args:
            level: 日志级别，默认ERROR及以上会触发上报
            format_string: 自定义格式字符串
        """
        if self._is_configured:
            return
            
        # 默认格式
        if format_string is None:
            format_string = (
                "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                "<level>{level: <8}</level> | "
                "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
                "<level>{message}</level>"
            )
        
        # 添加自定义handler用于上报
        logger.add(
            self._report_handler,
            level=level,
            format=format_string,
            filter=lambda record: record["extra"].get("report", False)
        )
        
        # 添加report方法到logger (使用bind方式避免类型检查错误)
        self._add_report_method()
        self._is_configured = True
    
    def _report_handler(self, message):
        """处理需要上报的日志消息"""
        record = message.record
        
        # 构建上报内容
        title = f"[{record['level'].name}] 系统日志上报"
        
        # 构建详细内容
        content_parts = [
            f"**时间**: {record['time'].strftime('%Y-%m-%d %H:%M:%S')}",
            f"**级别**: {record['level'].name}",
            f"**模块**: {record['name']}",
            f"**函数**: {record['function']}:{record['line']}",
            f"**消息**: {record['message']}"
        ]
        
        # 如果有异常信息，添加异常详情
        if record['exception']:
            content_parts.append(f"**异常**: {record['exception']}")
        
        # 添加额外的上报信息
        extra_info = record['extra'].get('report_info', {})
        if extra_info:
            for key, value in extra_info.items():
                content_parts.append(f"**{key}**: {value}")
        
        content = "\n\n".join(content_parts)
        
        # 发送通知
        try:
            self.notify.publish(title=title, content=content)
        except Exception as e:
            # 避免上报失败影响主程序
            print(f"日志上报失败: {e}", file=sys.stderr)
    
    def _add_report_method(self):
        """添加report方法到logger"""
        # 使用setattr动态添加方法，避免类型检查错误
        def report(message: str, level: str = "ERROR", **extra_info):
            """上报日志消息
            
            Args:
                message: 要上报的消息
                level: 日志级别
                **extra_info: 额外的上报信息
            """
            # 使用bind添加report标记和额外信息
            report_logger = logger.bind(report=True, report_info=extra_info)
            
            # 根据级别调用对应的日志方法
            level_method = getattr(report_logger, level.lower(), report_logger.error)
            level_method(message)
        
        # 动态添加方法
        setattr(logger, 'report', report)
    
    def _create_report_method(self):
        """创建report方法（保留用于兼容性）"""
        def report(message: str, level: str = "ERROR", **extra_info):
            """上报日志消息
            
            Args:
                message: 要上报的消息
                level: 日志级别
                **extra_info: 额外的上报信息
            """
            # 使用bind添加report标记和额外信息
            report_logger = logger.bind(report=True, report_info=extra_info)
            
            # 根据级别调用对应的日志方法
            level_method = getattr(report_logger, level.lower(), report_logger.error)
            level_method(message)
        
        return report
    
    @classmethod
    def from_settings(cls, settings: Dict[str, Any], level: str = "ERROR") -> 'LoguruReporter':
        """从配置创建LoguruReporter实例
        
        Args:
            settings: 通知渠道配置
            level: 日志级别
            
        Example:
            settings = {
                "BARK": {"token": "your token"},
                "WECHAT": {"token": "your token"},
            }
            reporter = LoguruReporter.from_settings(settings)
        """
        notify = Notify.from_settings(settings)
        reporter = cls(notify)
        reporter.configure_logger(level=level)
        return reporter


# 全局实例，方便直接使用
_global_reporter = None


def setup_loguru_reporter(settings: Optional[Dict[str, Any]] = None, 
                         channels: Optional[List] = None,
                         level: str = "ERROR") -> LoguruReporter:
    """设置全局loguru上报器
    
    Args:
        settings: 通知渠道配置字典
        channels: 通知渠道实例列表
        level: 日志级别
    
    Returns:
        LoguruReporter实例
    """
    global _global_reporter
    
    if settings:
        _global_reporter = LoguruReporter.from_settings(settings, level=level)
    elif channels:
        notify = Notify(channels)
        _global_reporter = LoguruReporter(notify)
        _global_reporter.configure_logger(level=level)
    else:
        _global_reporter = LoguruReporter()
        _global_reporter.configure_logger(level=level)
    
    return _global_reporter


def get_reporter() -> Optional[LoguruReporter]:
    """获取全局上报器实例"""
    return _global_reporter