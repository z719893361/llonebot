from __future__ import annotations

from abc import abstractmethod, ABC


class EventHandler(ABC):
    """
    事件处理器
    """
    @abstractmethod
    async def support(self, context: dict, state: dict) -> bool:
        """
        :param context:         当前事件上下文
        :param state:  全局上下文
        :return:
        """
        pass

    @abstractmethod
    async def handler(self, context: dict, state: dict) -> None:
        """
        :param context: 当前事件上下文
        :param state:  全局上下文
        :return:
        """
        pass
