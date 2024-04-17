import asyncio
from collections import deque
from typing import Callable, List, Annotated
from inspect import iscoroutinefunction, signature, Parameter

import aiocron
from loguru import logger

from onebot.filter.interfaces import Filter
from onebot.parameter.composite import parameters


class Route:
    def __init__(self, func: Callable, filters: List[Filter]):
        self.func = func
        self.filters = [] if filters is None else filters
        self.is_async = iscoroutinefunction(func)
        self.parameters = parameters.support_function(func)

    async def matches(self, scope: dict):
        for f in self.filters:
            if not await f.support(scope):
                return False
        return True

    async def handle(self, scope: dict, after_close: List[Parameter]):
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


class Event:
    def __init__(self, func: Callable, event_type: str):
        self.func: Callable = func
        self.event_type: str = event_type
        self.parameters = parameters.support_function(func)
        self.is_async = iscoroutinefunction(func)

    async def __call__(self, scope: dict, after_close: List[Parameter]):
        param_values = deque()
        for param in self.parameters:
            if await parameters.support(param, scope):
                param_values.append(await parameters.resolve(param, scope))
                after_close.append(param)
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

    def register(self, func: Callable, filters: List[Filter]):
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

    def on_event(
            self,
            event_type: str
    ):
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
    async def run_handlers(handlers: List[Callable], scope: dict):
        after_close = []
        for handler in handlers:
            try:
                await handler(scope, after_close)
            except Exception as e:
                logger.exception(e)
        for param in after_close:
            try:
                await parameters.close(param, {})
            except Exception as e:
                logger.exception(e)

    async def startup(self, scope: dict):
        await self.run_handlers(self.on_startup, scope)

    async def shutdown(self, scope: dict):
        await self.run_handlers(self.on_shutdown, scope)

    @staticmethod
    def crontab(func: Callable, spec: str, scope: dict):
        async def crontab():
            after_close = []
            param_value = []
            for param in parameter:
                param_value.append(await parameters.resolve(param, scope))
                after_close.append(param)
            else:
                if method_async_state:
                    await func(*param_value)
                else:
                    await asyncio.create_task(*param_value)
            for param in after_close:
                try:
                    await parameters.close(param, scope)
                except Exception as e:
                    logger.exception(e)
        # 预缓存参数列表
        parameter = parameters.support_function(func)
        # 方法异步状态
        method_async_state = iscoroutinefunction(func)
        # 启动定时任务
        aiocron.crontab(spec, crontab)
