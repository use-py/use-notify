# -*- coding: utf-8 -*-
"""
消息格式化器，负责格式化通知消息内容
"""

import json
from datetime import datetime
from typing import Any, Dict, Optional

from .context import ExecutionContext


class MessageFormatter:
    """消息格式化器"""

    DEFAULT_SUCCESS_TEMPLATE = (
        "✅ 函数 {function_name} 执行成功\n⏱️ 执行时间: {execution_time:.2f}秒"
    )
    DEFAULT_ERROR_TEMPLATE = (
        "❌ 函数 {function_name} 执行失败\n"
        "⏱️ 执行时间: {execution_time:.2f}秒\n"
        "🚨 错误信息: {error_message}"
    )

    def __init__(
        self,
        success_template: Optional[str] = None,
        error_template: Optional[str] = None,
        include_args: bool = False,
        include_result: bool = False,
    ):
        self.success_template = success_template or self.DEFAULT_SUCCESS_TEMPLATE
        self.error_template = error_template or self.DEFAULT_ERROR_TEMPLATE
        self.include_args = include_args
        self.include_result = include_result

    def format_success_message(self, context: ExecutionContext) -> Dict[str, str]:
        """格式化成功消息"""
        format_vars = self._get_format_variables(context)
        content = self.success_template.format(**format_vars)

        if self.include_result and context.result is not None:
            result_str = self._safe_serialize(context.result)
            content += f"\n📋 返回结果: {result_str}"

        return {"title": f"✅ {context.function_name} 执行成功", "content": content}

    def format_error_message(self, context: ExecutionContext) -> Dict[str, str]:
        """格式化错误消息"""
        format_vars = self._get_format_variables(context)
        content = self.error_template.format(**format_vars)

        return {"title": f"❌ {context.function_name} 执行失败", "content": content}

    def _get_format_variables(self, context: ExecutionContext) -> Dict[str, Any]:
        """获取格式化变量"""
        current_time = datetime.now()
        format_vars = {
            "function_name": context.function_name,
            "execution_time": context.execution_time or 0,
            "error_message": context.error_message,
            "start_time": context.start_time.strftime("%Y-%m-%d %H:%M:%S"),
            "current_time": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        }

        if context.end_time:
            format_vars["end_time"] = context.end_time.strftime("%Y-%m-%d %H:%M:%S")

        if self.include_args:
            format_vars["args"] = context.args
            format_vars["kwargs"] = context.kwargs

            # 添加安全的参数字符串表示
            args_str = self._safe_serialize(context.args)
            kwargs_str = self._safe_serialize(context.kwargs)
            format_vars["args_str"] = args_str
            format_vars["kwargs_str"] = kwargs_str

        if context.result is not None:
            format_vars["result"] = context.result
            format_vars["result_str"] = self._safe_serialize(context.result)

        return format_vars

    def _safe_serialize(self, obj: Any, max_length: int = 200) -> str:
        """安全序列化对象为字符串"""
        try:
            if obj is None:
                return "None"

            # 尝试 JSON 序列化
            try:
                result = json.dumps(obj, ensure_ascii=False, default=str)
            except (TypeError, ValueError):
                # 如果 JSON 序列化失败，使用 str()
                result = str(obj)

            # 限制长度
            if len(result) > max_length:
                result = result[:max_length] + "..."

            return result
        except Exception:
            return "<无法序列化>"
