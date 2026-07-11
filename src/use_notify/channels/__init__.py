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

CHANNEL_REGISTRY = {
    "bark": Bark,
    "chanify": Chanify,
    "console": Console,
    "ding": Ding,
    "email": Email,
    "feishu": Feishu,
    "ntfy": Ntfy,
    "pushdeer": PushDeer,
    "pushover": PushOver,
    "wechat": WeChat,
    "wecom": WeChat,
}


def get_channel_class(name):
    return CHANNEL_REGISTRY.get(name.lower())
