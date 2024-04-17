from abc import ABC, abstractmethod


class Filter(ABC):
    """
    消息过滤器
    """
    @abstractmethod
    async def support(self, scope: dict):
        pass
