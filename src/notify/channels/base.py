from abc import ABCMeta, abstractmethod
from usepy import useAdDict


class BaseChannel(metaclass=ABCMeta):

    def __init__(self, config: dict):
        self.config = useAdDict(config)

    @abstractmethod
    def send(self, message):
        raise NotImplementedError
