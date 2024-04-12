from inspect import Parameter
from typing import Any

from onebot.parameter.interfaces import Resolver


class AppResolver(Resolver):
    """
    主程序参数注入
    """

    def support_parameter(self, parameter: Parameter) -> bool:
        from onebot.application import OneBot
        return parameter.annotation is OneBot

    async def support_resolver(self, parameter: Parameter, message: dict, context: dict) -> bool:
        return True

    async def resolver(self, parameter: Parameter, app, message: dict, context: dict) -> Any:
        return app
