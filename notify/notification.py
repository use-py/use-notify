# -*- coding: utf-8 -*-
from abc import abstractmethod, ABCMeta

from .addict import Dict
from .utils import import_object, sort_dict_by_value


class Notification(metaclass=ABCMeta):

    @abstractmethod
    def send_message(self, content, title=None):
        ...


class Notify(Notification):
    """消息通知分发入口"""
    def __init__(self, triggers, channels):
        self.triggers = triggers
        self.channels = Dict(channels)

    def send_message(self, content, title=None):
        channels = self._create_channels()
        for channel in channels:
            notify = channel.from_settings(self.channels)
            notify.send_message(content=content, title=title)

    def _create_channels(self):
        if isinstance(self.triggers, dict):
            self.triggers = sort_dict_by_value(self.triggers, reverse=False)
            objs = [import_object(trigger[0]) for trigger in self.triggers.items()]
        elif isinstance(self.triggers, list):
            objs = [import_object(trigger[0]) for trigger in self.triggers]
        elif isinstance(self.triggers, str):
            objs = [import_object(self.triggers)]
        else:
            raise TypeError("triggers type error")
        return objs

    @classmethod
    def from_settings(cls, settings=None):
        if settings is None:
            from . import default_settings
            settings = default_settings
        return cls(settings.TRIGGERS, settings.CHANNELS)
