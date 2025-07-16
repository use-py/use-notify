# -*- coding: utf-8 -*-
"""
执行上下文类，记录函数执行信息
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional


@dataclass
class ExecutionContext:
    """函数执行上下文信息"""
    function_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    args: tuple = field(default_factory=tuple)
    kwargs: dict = field(default_factory=dict)
    result: Any = None
    exception: Optional[Exception] = None
    execution_time: Optional[float] = None
    
    def mark_success(self, result: Any) -> None:
        """标记执行成功"""
        self.end_time = datetime.now()
        self.result = result
        self.execution_time = (self.end_time - self.start_time).total_seconds()
    
    def mark_error(self, exception: Exception) -> None:
        """标记执行失败"""
        self.end_time = datetime.now()
        self.exception = exception
        self.execution_time = (self.end_time - self.start_time).total_seconds()
    
    @property
    def is_success(self) -> bool:
        """是否执行成功"""
        return self.exception is None
    
    @property
    def error_message(self) -> str:
        """错误信息"""
        if self.exception:
            return str(self.exception)
        return ""