# -*- coding: utf-8 -*-
from loguru import logger
from notify.notification import Notification


class Custom(Notification):
    """自定义消息"""
    def __init__(self, settings):
        self.settings = settings

    def send_message(self, content, title=None):
        logger.debug(f"来自自定义的消息{content}")

    @classmethod
    def from_settings(cls, settings):
        return cls(settings)