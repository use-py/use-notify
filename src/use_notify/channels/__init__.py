# flake8: noqa: F401
from .console import Console
from .bark import Bark
from .base import BaseChannel
from .chanify import Chanify
from .ding import Ding
from .email import Email
from .pushdeer import PushDeer
from .pushover import PushOver
from .wechat import WeChat

# 兼容wecom
WeCom = WeChat
