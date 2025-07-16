# -*- coding: utf-8 -*-
"""
装饰器异常类定义
"""


class NotifyDecoratorError(Exception):
    """装饰器基础异常类"""
    pass


class NotifyConfigError(NotifyDecoratorError):
    """配置错误异常"""
    pass


class NotifySendError(NotifyDecoratorError):
    """通知发送错误异常"""
    pass