# -*- coding: utf-8 -*-
"""
Loguru类型扩展

这个文件提供了loguru logger的类型扩展，用于支持report方法的类型检查
"""

from typing import Any, Protocol
from loguru import Logger as _Logger


class ReportMethod(Protocol):
    """Report方法的协议定义"""
    
    def __call__(self, message: str, level: str = "ERROR", **extra_info: Any) -> None:
        """上报日志消息
        
        Args:
            message: 要上报的消息
            level: 日志级别
            **extra_info: 额外的上报信息
        """
        ...


class ExtendedLogger(_Logger):
    """扩展的Logger类，包含report方法"""
    
    report: ReportMethod
    
    def report(self, message: str, level: str = "ERROR", **extra_info: Any) -> None:
        """上报日志消息
        
        Args:
            message: 要上报的消息
            level: 日志级别（INFO, WARNING, ERROR, CRITICAL）
            **extra_info: 额外的上报信息
        
        Example:
            logger.report("系统错误", level="ERROR", 服务器="web-01")
        """
        ...


# 类型别名
LoggerWithReport = ExtendedLogger