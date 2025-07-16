# flake8: noqa: F401
from . import channels as useNotifyChannel
from .notification import Notify as useNotify
from .loguru_integration import LoguruReporter, setup_loguru_reporter, get_reporter

# 类型定义（用于类型检查）
try:
    from .loguru_types import ExtendedLogger, LoggerWithReport
except ImportError:
    # 如果导入失败，定义空的类型别名
    ExtendedLogger = None
    LoggerWithReport = None
