"""
参数注入模板
"""

from abc import abstractmethod, ABC
from inspect import Parameter
from typing import Any


class Resolver(ABC):
    """
    参数解析器接口

    该接口定义了参数解析器的基本方法，用于判断参数是否由该解析器解析、
    当前请求的参数是否支持解析以及进行参数解析的具体实现。
    """

    @abstractmethod
    def support_parameter(self, parameter: Parameter) -> bool:
        """
        判断参数是否由该解析器解析

        :param parameter: 参数，inspect.Parameter 对象，表示函数或方法的参数
        :return: bool，如果该解析器支持解析指定的参数，则返回 True；否则返回 False
        """
        pass

    @abstractmethod
    async def support_resolver(self, parameter: Parameter, context: dict, state: dict) -> bool:
        """
        判断当前请求的参数是否支持解析

        :param parameter: 参数，inspect.Parameter 对象
        :param context: 上下文，字典类型，表示当前请求的上下文信息
        :param state: 全局上下文
        :return: bool，如果当前请求的参数支持解析，则返回 True；否则返回 False
        """
        pass

    @abstractmethod
    async def resolver(self, parameter: Parameter, context: dict, state: dict) -> Any:
        """
        参数解析方法

        :param parameter: 参数，inspect.Parameter 对象
        :param context: 上下文，字典类型，表示当前请求的上下文信息
        :param state: 全局上下文

        :return: 解析后的参数值，类型依赖于参数解析的具体实现
        """
        pass

    async def close(self, parameter, context: dict, global_context: dict):
        """
        单次请求结束后调用的函数

        :param parameter: 参数，inspect.Parameter 对象
        :param context: 上下文，字典类型，表示当前请求的上下文信息
        :param global_context: 全局上下文
        :return: 无返回值
        """
        pass


class Depend(ABC):
    """
    参数注入接口

    该接口定义了参数注入的基本方法，用于判断当前请求的参数是否支持解析以及进行参数解析的具体实现。
    """

    @abstractmethod
    async def support(self, message: dict, context: dict) -> bool:
        """
        判断是否支持解析当前请求的参数

        该方法用于判断给定的消息和上下文信息是否满足解析条件。

        :param message: 消息，字典类型，表示当前处理的消息数据
        :param context: 上下文，字典类型，表示当前请求的上下文信息
        :return: bool，如果支持解析，则返回 True；否则返回 False
        """
        pass

    @abstractmethod
    async def resolver(self, parameter: Parameter, app, message: dict, context: dict) -> Any:
        """
        参数解析方法

        该方法用于根据给定的参数、应用程序实例、消息和上下文信息解析出实际的参数值。

        :param parameter: 参数，inspect.Parameter 对象，表示函数或方法的参数
        :param app: 主程序，通常是应用程序或框架的实例
        :param message: 消息，字典类型，表示当前处理的消息数据
        :param context: 上下文，字典类型，表示当前请求的上下文信息
        :return: 解析后的参数值，类型依赖于参数解析的具体实现
        """
        pass

    async def close(self, parameter: Parameter, context: dict):
        """
        单次请求结束后调用的函数

        该方法在每次请求结束后调用，用于执行清理操作或资源释放。

        :param parameter: 参数，inspect.Parameter 对象
        :param context: 上下文，字典类型，表示当前请求的上下文信息
        :return: 无返回值
        """
        pass
