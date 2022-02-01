# -*- coding: utf-8 -*-
import logging
from notify.notification import Notification

logger = logging.getLogger(__name__)


class Custom(Notification):
    """自定义消息"""
    def __init__(self, settings):
        self.settings = settings

    def send_message(self, content, title=None):
        logger.debug(f"来自自定义的消息{content}")

    @classmethod
    def from_settings(cls, settings):
        return cls(settings)