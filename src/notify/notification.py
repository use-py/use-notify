# -*- coding: utf-8 -*-
from typing import Optional, List

from .channels import BaseChannel


class Publisher:

    def __init__(self, channels: Optional[List[BaseChannel]] = None):
        if channels is None:
            channels = []
        self.channels = channels

    def add(self, *channels):
        for channel in channels:
            self.channels.append(channel)

    def publish(self, *args, **kwargs):
        for channel in self.channels:
            channel.send(*args, **kwargs)


class Notify(Publisher):
    pass
