# flake8: noqa: F401
from .console import Console
from .bark import Bark
from .base import BaseChannel
from .chanify import Chanify
from .ding import Ding
from .email import Email
from .ntfy import Ntfy
from .pushdeer import PushDeer
from .pushover import PushOver
from .wechat import WeChat
from .feishu import Feishu

# 兼容wecom
WeCom = WeChat
