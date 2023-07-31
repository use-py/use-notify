# -*- coding: utf-8 -*-
import asyncio
from typing import Optional, List

from .channels import BaseChannel


class Publisher:
    """A class that publishes notifications to multiple channels."""

    def __init__(self, channels: Optional[List[BaseChannel]] = None):
        if channels is None:
            channels = []
        self.channels = channels

    def add(self, *channels):
        """
        Add channels to the Publisher.

        Args:
            *channels: Variable number of BaseChannel objects.
        """
        for channel in channels:
            self.channels.append(channel)

    def publish(self, *args, **kwargs):
        """
        Publish a notification to all channels.
        """
        for channel in self.channels:
            channel.send(*args, **kwargs)

    async def publish_async(self, *args, **kwargs):
        """
        Publish a notification asynchronously to all channels.
        """
        tasks = [
            channel.send_async(*args, **kwargs)
            for channel in self.channels
        ]
        await asyncio.gather(*tasks)


class Notify(Publisher):
    """A subclass of Publisher that represents a notification publisher."""
    pass
