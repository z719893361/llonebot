from __future__ import annotations

from abc import abstractmethod, ABC


class EventHandler(ABC):
    """
    事件处理器
    """
    @abstractmethod
    async def support(self, app, message: dict, context: dict) -> bool:
        pass

    @abstractmethod
    async def handler(self, app, message: dict, context: dict) -> None:
        pass
