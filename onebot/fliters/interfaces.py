from __future__ import annotations

from abc import abstractmethod, ABC


class Filter(ABC):
    """
    过滤器接口
    """

    @abstractmethod
    async def support(self, app, message: dict, context: dict) -> bool:
        pass
