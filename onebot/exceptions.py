from inspect import Parameter, getfile
from typing import Callable


class SendMessageError(Exception):
    """
    发送消息错误
    """

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class BuildMessageError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class RegisterTaskError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class ParameterError(Exception):
    def __init__(self, message: str, fn: Callable, parameter: Parameter):
        self.msg = message
        self.fn = fn
        self.parameter = parameter

    def __str__(self):
        return f"{self.msg}, 函数: {self.fn.__name__} 参数: {self.parameter.name} 文件: {getfile(self.fn)}"


class AuthenticationError(Exception):
    """
    用于认证过程中出现的错误的异常。

    属性:
        message (str): 错误的解释，默认为"Token认证失败"。

    方法:
        __init__: 构造AuthenticationError对象所需的所有属性。
    """

    def __init__(self, message="Token认证失败"):
        """
        使用可选的自定义消息初始化AuthenticationError。

        参数:
            message (str): 描述认证失败的自定义错误消息，默认为"Token认证失败"。
        """
        self.message = message
        super().__init__(self.message)
