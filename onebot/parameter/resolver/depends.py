import asyncio
from inspect import Parameter, iscoroutinefunction
from typing import Any

from onebot.parameter.interfaces import Resolver, Depend


class DependsResolver(Resolver):
    """
    Depends处理器
    """

    def __init__(self):
        self.method_async_status = {}

    def support_parameter(self, parameter: Parameter):
        return isinstance(parameter.default, Depend)

    async def support_resolver(self, parameter: Parameter, context: dict, state: dict) -> bool:
        support = parameter.default.support
        if support not in self.method_async_status:
            self.method_async_status[support] = iscoroutinefunction(support)
        if self.method_async_status[support]:
            return await support(context['request'], context)
        else:
            return await asyncio.to_thread(support, context['request'], context)

    async def resolver(self, parameter: Parameter, context: dict, state: dict) -> Any:
        resolver = parameter.default.resolver
        if resolver not in self.method_async_status:
            self.method_async_status[resolver] = iscoroutinefunction(resolver)
        if self.method_async_status[resolver]:
            return await resolver(parameter, state['app'], context['request'], context)
        else:
            return await asyncio.to_thread(resolver, parameter, state['app'], context['request'], context)

    async def close(self, parameter, context: dict, global_context: dict):
        close = parameter.default.close
        if close not in self.method_async_status:
            self.method_async_status[close] = iscoroutinefunction(close)
        if self.method_async_status[close]:
            return await close(parameter, context)
        else:
            return await asyncio.to_thread(close, parameter, context)
