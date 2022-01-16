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
    def __init__(self, settings):
        if settings is None:
            from . import default_settings
            settings = default_settings
        self.settings = settings
        self.triggers = self.settings.TRIGGERS
        self.channels = Dict(self.settings.CHANNELS)

    def send_message(self, content, title=None):
        self.triggers = sort_dict_by_value(self.triggers, reverse=False)
        objs = [import_object(trigger[0]) for trigger in self.triggers.items()]
        for obj in objs:
            notify = obj.from_settings(self.channels)
            notify.send_message(content=content, title=title)

    @classmethod
    def from_settings(cls, settings=None):
        return cls(settings)
