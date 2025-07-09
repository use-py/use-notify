# -*- coding: utf-8 -*-
import asyncio
from typing import List, Optional

from use_notify import channels as channels_models


class Publisher:
    """A class that publishes notifications to multiple channels."""

    def __init__(self, channels: Optional[List[channels_models.BaseChannel]] = None):
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
        tasks = [channel.send_async(*args, **kwargs) for channel in self.channels]
        await asyncio.gather(*tasks)


class Notify(Publisher):
    """A subclass of Publisher that represents a notification publisher."""

    @classmethod
    def from_settings(cls, settings: dict):
        """
        Create a Notify instance from a settings object.

        Args:
            settings: A settings object.
        Example:
            settings = {
            ...     "BARK": {"token": "your token"},
            ...     "DINGTALK": {"access_token": "your access token"},
            ... }
            notify = Notify.from_settings(settings)
            notify.publish(title="消息标题", content="消息正文")

        Returns:
            A Notify instance.
        """
        channels = []
        for channel, cfg in settings.items():
            # Try to get class by case-insensitive match
            channel_cls = None
            for cls_name in dir(channels_models):
                if cls_name.lower() == channel.lower():
                    channel_cls = getattr(channels_models, cls_name)
                    break
            if not channel_cls:
                raise ValueError(f"Unknown channel {channel}")
            channel = channel_cls(cfg)
            channels.append(channel)
        return cls(channels)
