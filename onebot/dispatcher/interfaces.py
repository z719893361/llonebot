from abc import ABC, abstractmethod


class EventDispatcher(ABC):
    """
    消息过滤器
    """
    @abstractmethod
    async def support(self, scope: dict):
        pass

    @abstractmethod
    async def handle(self, scope: dict):
        pass
    