import asyncio
from typing import Callable, List, Tuple
from inspect import iscoroutinefunction, Parameter

import aiocron
from loguru import logger

from onebot.filter.interfaces import FilterInterface
from onebot.parameter import Resolver
from onebot.parameter.composite import PARAMETER_RESOLVER


class Route:
    def __init__(self, func: Callable, filters: List[FilterInterface], order: int, continue_: bool):
        self.func = func
        self.filters = filters
        self.is_async = iscoroutinefunction(func)
        self.resolvers = PARAMETER_RESOLVER.get_function_resolvers(func)
        self.order = order
        self.continue_ = continue_

    async def matches(self, scope: dict):
        for f in self.filters:
            if not await f.support(scope):
                return False
        return True

    async def handle(self, scope: dict, param_close: List[Tuple[Parameter, Resolver]]):
        param_value = []
        for param, resolver in self.resolvers:
            if not await resolver.support(param, scope):
                return
            param_value.append(await resolver.resolve(param, scope))
            param_close.append((param, resolver))
        else:
            if self.is_async:
                await self.func(*param_value)
            else:
                await asyncio.to_thread(self.func, *param_value)


class Event:
    def __init__(self, func: Callable, event_type: str):
        self.func: Callable = func
        self.event_type: str = event_type
        self.parameters = PARAMETER_RESOLVER.get_parameter_resolver(func)
        self.is_async = iscoroutinefunction(func)

    async def __call__(self, scope: dict, after_close_param: List[Parameter]):
        param_values = []
        for param in self.parameters:
            if await PARAMETER_RESOLVER.support(param, scope):
                param_values.append(await PARAMETER_RESOLVER.resolve(param, scope))
                after_close_param.append(param)
            else:
                param_values.append(None)
        if self.is_async:
            await self.func(*param_values)
        else:
            await asyncio.to_thread(self.func, *param_values)


class Router:
    def __init__(self):
        self.routes: List[Route] = []
        self.on_startup: List[Event] = []
        self.on_shutdown: List[Event] = []

    def register(self, func: Callable, filters: List[FilterInterface], order: int, continue_: bool):
        route = Route(
            func=func,
            filters=filters,
            order=order,
            continue_=continue_
        )
        self.routes.append(route)
        self.routes.sort(key=lambda r: r.order)

    async def __call__(self, scope: dict):
        after_close_param = []
        exc = None
        try:
            for route in self.routes:
                if await route.matches(scope):
                    await route.handle(scope, after_close_param)
                    if not route.continue_:
                        break
        except Exception as e:
            logger.exception(e)
            exc = e
        for param, resolver in after_close_param:
            try:
                await resolver.close(param, scope, exc)
            except Exception as e:
                logger.exception(e)

    def on_event(self, event_type: str):
        def decorator(func: Callable) -> Callable:
            self.add_event_handler(event_type, func)
            return func

        return decorator

    def add_event_handler(self, event_type, func):
        assert event_type in ("startup", "shutdown")
        event = Event(func, event_type)
        if event_type == "startup":
            self.on_startup.append(event)
        else:
            self.on_shutdown.append(event)

    @staticmethod
    async def run_event_handlers(handlers: List[Callable], scope: dict):
        after_close_param = []
        for handler in handlers:
            try:
                await handler(scope, after_close_param)
            except Exception as e:
                logger.exception(e)
        for param, resolver in after_close_param:
            try:
                await resolver.close(param, {})
            except Exception as e:
                logger.exception(e)

    async def startup(self, scope: dict):
        await self.run_event_handlers(self.on_startup, scope)

    async def shutdown(self, scope: dict):
        await self.run_event_handlers(self.on_shutdown, scope)

    @staticmethod
    def crontab(func: Callable, spec: str, scope: dict):
        async def crontab():
            param_value = []
            for param, resolver in parameter_resolver:
                param_value.append(await resolver.resolve(param, scope))
            else:
                if method_async_state:
                    await func(*param_value)
                else:
                    await asyncio.create_task(*param_value)
            for param, resolver in parameter_resolver:
                try:
                    await resolver.close(param, scope)
                except Exception as e:
                    logger.exception(e)

        # 预缓存参数列表
        parameter_resolver = PARAMETER_RESOLVER.get_function_resolvers(func)
        # 方法是否为异步
        method_async_state = iscoroutinefunction(func)
        # 启动定时任务
        aiocron.crontab(spec, crontab)
