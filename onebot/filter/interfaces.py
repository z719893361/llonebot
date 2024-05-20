from abc import ABC, abstractmethod


class FilterInterface(ABC):
    """
    消息过滤器
    """
    @abstractmethod
    async def support(self, scope: dict):
        pass
