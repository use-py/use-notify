# flake8: noqa: F401
from .bark import Bark
from .base import BaseChannel
from .chanify import Chanify
from .console import Console
from .ding import Ding
from .email import Email
from .feishu import Feishu
from .ntfy import Ntfy
from .pushdeer import PushDeer
from .pushover import PushOver
from .wechat import WeChat

# 兼容wecom
WeCom = WeChat
