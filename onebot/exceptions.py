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
