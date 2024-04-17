from inspect import Parameter
from typing import Any

from onebot.parameter.interfaces import Resolver


class AppResolver(Resolver):
    def support_parameter(self, parameter: Parameter) -> bool:
        from onebot import OneBot
        return parameter.annotation == OneBot

    async def support(self, parameter: Parameter, scope: dict) -> bool:
        return 'app' in scope

    async def resolve(self, parameter: Parameter, scope: dict) -> Any:
        return scope.get('app')
