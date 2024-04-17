class ParameterError(Exception):
    def __init__(self, msg, func, param):
        self.msg = msg
        self.func = func
        self.param = param

    def __str__(self):
        return f"{self.msg}, 函数: {self.func.__name__} 参数: {self.param.name}"


class AuthenticationError(Exception):
    def __init__(self):
        super().__init__("认证失败")


class BuildMessageError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg
    