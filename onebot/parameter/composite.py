from inspect import Parameter, signature
from typing import Any, List, Dict, Set, Callable, Tuple

from onebot.exceptionals import ParameterError
from onebot.parameter.interfaces import Resolver

from onebot.parameter.resolver.app import AppResolver
from onebot.parameter.resolver.dependency import DependencyResolver


class ResolverComposite:
    """
    参数解析器组合器
    """

    def __init__(self):
        # 解析器
        self.argument_resolves: List[Resolver] = []
        # 可解析方法缓存
        self.func_resolvers_cache: Dict[Callable, List[Tuple[Parameter, Resolver]]] = {}
        # 不可解析方法缓存
        self.func_unsupported: Set[Callable] = set()

    def get_parameter_resolver(self, parameter: Parameter):
        for resolver in self.argument_resolves:
            if resolver.support_parameter(parameter):
                return resolver

    def get_function_resolvers(self, func: Callable) -> List[Tuple[Parameter, Resolver]]:
        """
        获取方法的参数和对应的解析器
        :param func:
        :return:
        """
        if func in self.func_resolvers_cache:
            return self.func_resolvers_cache[func]
        resolvers = []
        for param in signature(func).parameters.values():
            resolver = self.get_parameter_resolver(param)
            if resolver:
                resolvers.append((param, resolver))
            else:
                raise ParameterError('参数不支持解析', func, param)
        self.func_resolvers_cache[func] = resolvers
        return resolvers

    def add_resolve(self, resolver: Resolver):
        """
        添加参数解决器
        :param resolver: 解决器
        """
        self.argument_resolves.append(resolver)


PARAMETER_RESOLVER = ResolverComposite()
PARAMETER_RESOLVER.add_resolve(AppResolver())
PARAMETER_RESOLVER.add_resolve(DependencyResolver())
