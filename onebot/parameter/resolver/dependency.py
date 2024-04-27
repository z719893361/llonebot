from inspect import Parameter
from typing import Any

from onebot.parameter.interfaces import Resolver, Dependency


class DependencyResolver(Resolver):
    def support_parameter(self, parameter: Parameter) -> bool:
        return isinstance(parameter.default, Dependency)

    async def support(self, parameter: Parameter, scope: dict) -> bool:
        return await parameter.default.support(parameter, scope)

    async def resolve(self, parameter: Parameter, scope: dict) -> Any:
        return await parameter.default.resolve(parameter, scope)

    async def close(self, parameter: Parameter, scope: dict, exc: Exception):
        await parameter.default.close(parameter, scope, exc)
