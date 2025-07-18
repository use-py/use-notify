from abc import ABCMeta, abstractmethod

from usepy.dict import AdDict


class BaseChannel(metaclass=ABCMeta):
    def __init__(self, config: dict):
        self.config = AdDict(config)

    @abstractmethod
    def send(self, content, title=None):
        raise NotImplementedError

    @abstractmethod
    async def send_async(self, content, title=None):
        raise NotImplementedError
