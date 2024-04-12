"""
参数注入模板
"""

from abc import abstractmethod, ABC
from inspect import Parameter
from typing import Any


class Resolver(ABC):
    """
    参数解析器接口
    """

    @abstractmethod
    def support_parameter(self, parameter: Parameter) -> bool:
        """
        参数是否由该解析器解析
        :param parameter:   参数
        :return:  是否支持
        """
        pass

    @abstractmethod
    async def support_resolver(self, parameter: Parameter, message: dict, context: dict) -> bool:
        """
        当前请求该参数是否支持解析
        :param parameter:   参数
        :param message:     消息
        :param context:     上下文
        :return:  是否支持
        """
        pass

    @abstractmethod
    async def resolver(self, parameter: Parameter, app, message: dict, context: dict) -> Any:
        """
        参数解析
        :param parameter:   参数
        :param app:         主程序
        :param message:     消息
        :param context:     上下文
        :return:
        """
        pass

    async def close(self, parameter, context: dict):
        """
        单次请求结束后调用函数
        :param parameter:   参数
        :param context:     上下文
        :return:
        """
        pass


class Depend(ABC):
    """
    参数注入接口
    """

    @abstractmethod
    async def support(self, message: dict, context: dict) -> bool:
        """
        是否支持解析
        :param message:
        :param context:
        :return:
        """
        pass

    @abstractmethod
    async def resolver(self, parameter: Parameter, app, message: dict, context: dict) -> Any:
        """
        参数解析
        :param parameter:   参数
        :param app:         主程序
        :param message:     消息
        :param context:     上下文
        :return:            结果
        """
        pass

    async def close(self, parameter: Parameter, context: dict):
        """
        单次请求结束后调用函数
        :param parameter:
        :param context:
        :return:
        """
        pass
