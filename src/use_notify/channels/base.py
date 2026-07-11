from abc import ABCMeta, abstractmethod

from usepy.dict import AdDict


class BaseChannel(metaclass=ABCMeta):
    def __init__(self, config: dict):
        self.config = AdDict(config)

    def resolve_config_value(self, field):
        value = getattr(self.config, field)
        return value() if callable(value) else value

    @abstractmethod
    def send(self, content, title=None):
        raise NotImplementedError

    @abstractmethod
    async def send_async(self, content, title=None):
        raise NotImplementedError
