import asyncio
from inspect import Parameter, iscoroutinefunction, signature
from typing import List, Dict, Set, Any, Callable

from .interfaces import Resolver
from .resolver.app import AppResolver
from .resolver.depends import DependsResolver
from ..exceptions import ParameterError


class ResolverComposite(Resolver):
    """
    参数解析器组合器
    """

    def __init__(self):
        # 解析器
        self.argument_resolves: List[Resolver] = []
        # 可解析参数缓存
        self.argument_resolve_cache: Dict[Parameter, Resolver] = {}
        # 不可解析参数缓存
        self.unresolvable_param: Set[Parameter] = set()
        # 是否为异步函数
        self.func_async_status = {}

        self.loop = asyncio.get_event_loop()

    def get_parameter_resolve(self, parameter):
        """
        获取参数解析器
        :param parameter: 参数
        :return: 参数解析器
        """
        if parameter in self.unresolvable_param:
            return
        if parameter in self.argument_resolve_cache:
            return self.argument_resolve_cache.get(parameter)
        for resolver in self.argument_resolves:
            if resolver.support_parameter(parameter):
                self.argument_resolve_cache[parameter] = resolver
                return resolver
        self.unresolvable_param.add(parameter)

    def support_parameter(self, parameter: Parameter):
        """
        该参数是否由该解析器解析
        :param parameter:
        :return:
        """
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

    async def support_resolver(self, parameter: Parameter, context: dict, state: dict) -> bool:
        """
        该参数是否支持解析
        :param parameter: 参数
        :param context: 上下文
        :param state: 全局上下文
        :return:
        """
        support_resolver = self.get_parameter_resolve(parameter).support_resolver
        if support_resolver not in self.func_async_status:
            self.func_async_status[support_resolver] = iscoroutinefunction(support_resolver)
        if self.func_async_status[support_resolver]:
            return await support_resolver(parameter, context, state)
        else:
            return await self.loop.run_in_executor(None, resolver, message, context)  # type: ignore

    async def resolver(self, parameter: Parameter, context: dict, state: dict) -> Any:
        resolver = self.argument_resolve_cache.get(parameter).resolver
        if resolver not in self.func_async_status:
            self.func_async_status[resolver] = iscoroutinefunction(resolver)
        if self.func_async_status[resolver]:
            return await resolver(parameter, context, state)
        else:
            return await self.loop.run_in_executor(None, resolver, parameter, context, state)

    async def close(self, parameter, context: dict, state: dict):
        """
        关闭函数
        :param parameter: 参数
        :param context: 上下文
        :param state: 全局上下文
        """
        close = self.get_parameter_resolve(parameter).close
        if close not in self.func_async_status:
            self.func_async_status[close] = iscoroutinefunction(close)
        if self.func_async_status[close]:
            return await close(parameter, context, state)
        else:
            return await self.loop.run_in_executor(None, close, parameter, context, state)

    def add_resolve(self, resolver: Resolver):
        """
        添加参数解决器
        :param resolver: 解决器
        """
        self.argument_resolves.append(resolver)


parameter_resolver = ResolverComposite()
parameter_resolver.add_resolve(AppResolver())
parameter_resolver.add_resolve(DependsResolver())
