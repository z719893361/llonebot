from inspect import Parameter, signature
from typing import Any, List, Dict, Set, Callable

from onebot.exceptionals import ParameterError
from onebot.parameter.interfaces import Resolver

from onebot.parameter.resolver.app import AppResolver
from onebot.parameter.resolver.dependency import DependencyResolver


class ResolverComposite(Resolver):
    """
    参数解析器组合器
    """

    def __init__(self):
        # 解析器
        self.argument_resolves: List[Resolver] = []
        # 可解析参数缓存
        self.resolver_cache: Dict[Parameter, Resolver] = {}
        # 不可解析参数缓存
        self.unsupported_parameters: Set[Parameter] = set()

    def get_parameter_resolve(self, parameter):
        if parameter in self.resolver_cache:
            return self.resolver_cache[parameter]
        if parameter in self.unsupported_parameters:
            return
        for resolver in self.argument_resolves:
            if resolver.support_parameter(parameter):
                self.resolver_cache[parameter] = resolver
                return resolver
        self.unsupported_parameters.add(parameter)

    def support_parameter(self, parameter: Parameter):
        return self.get_parameter_resolve(parameter) is not None

    def support_function(self, fn: Callable):
        """
        检查函数参数是否支持解析
        :param fn: 函数
        :return:
        """
        arguments = signature(fn).parameters.values()
        for param in arguments:
            if not self.support_parameter(param):
                raise ParameterError('参数不支持解析', fn, param)
        return arguments

    async def support(self, parameter: Parameter, scope: dict) -> bool:
        return await self.get_parameter_resolve(parameter).support(parameter, scope)

    async def resolve(self, parameter: Parameter, scope: dict) -> Any:
        return await self.get_parameter_resolve(parameter).resolve(parameter, scope)

    async def close(self, parameter, scope: dict):
        await self.get_parameter_resolve(parameter).close(parameter, scope)

    def add_resolve(self, resolver: Resolver):
        """
        添加参数解决器
        :param resolver: 解决器
        """
        self.argument_resolves.append(resolver)


parameters = ResolverComposite()
parameters.add_resolve(AppResolver())
parameters.add_resolve(DependencyResolver())
