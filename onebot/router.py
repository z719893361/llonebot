import asyncio
import time
from collections import deque
from typing import Callable, List
from inspect import iscoroutinefunction, signature, Parameter

from loguru import logger

from onebot.filter.interfaces import Filter
from onebot.parameter.composite import parameters


class Route:
    def __init__(self, func: Callable, filters: List[Filter]):
        self.func = func
        self.filters = [] if filters is None else filters
        self.is_async = iscoroutinefunction(func)
        self.parameters = signature(func).parameters.values()

    async def matches(self, scope: dict):
        for f in self.filters:
            if not await f.support(scope):
                return False
        return True

    async def handle(self, scope: dict, after_close: List[Parameter]):
        """
        :param scope:        上下文信息
        :param after_close:  生命周期后关闭参数
        :return:
        """
        param_values = deque()
        for param in self.parameters:
            if await parameters.support(param, scope):
                param_values.append(await parameters.resolve(param, scope))
            else:
                return
            after_close.append(param)
        if self.is_async:
            await self.func(*param_values)
        else:
            await asyncio.to_thread(self.func, *param_values)


class Router:
    def __init__(self):
        self.routes = []

    def register(self, func: Callable, filters: List[Filter]):
        parameters.support_function(func)
        route = Route(
            func=func,
            filters=filters
        )
        self.routes.append(route)

    async def __call__(self, scope: dict):
        after_close: List[Parameter] = []
        for route in self.routes:
            try:
                if await route.matches(scope):
                    await route.handle(scope, after_close)
            except Exception as e:
                logger.exception(e)
        # 生命周期结束
        for param in after_close:
            try:
                await parameters.close(param, scope)
            except Exception as e:
                logger.exception(e)
