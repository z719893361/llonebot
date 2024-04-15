from __future__ import annotations

from abc import abstractmethod, ABC


class Filter(ABC):
    """
    过滤器接口
    """

    @abstractmethod
    async def support(self, context: dict, state: dict) -> bool:
        """

        :param context: 请求上下文
        :param state: 全局上下文
        :return:
        """
        pass
