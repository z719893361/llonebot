from __future__ import annotations

import asyncio
from collections import deque
from dataclasses import dataclass
from inspect import iscoroutinefunction, Parameter
from typing import Callable, List, Dict, ValuesView

import aiocron
from loguru import logger

from onebot.exceptions import ParameterError
from onebot.parameter import parameter_resolver
from onebot.fliters import Filter


@dataclass
class Config:
    # 回调函数
    func: Callable
    # 过滤器
    filters: List[Filter]
    # 优先级
    order: int
    # 首次匹配成功是否结束匹配
    first_over: bool
    # 是否允许空值，True参数解析为None会抛出异常
    nullable: bool
    # 如果允许空值，True参数解析时存在None则跳过函数调用，False则继续调用
    skipnull: bool


class HandlerManager:
    """
    事件管理器
    """

    def __init__(self):
        self.handlers: List[Config] = []
        # 方法参数缓存
        self.method_parameters: Dict[Callable, ValuesView[Parameter]] = {}
        # 是否异步函数缓存
        self.method_async_state: Dict[Callable, bool] = {}

        self.loop = asyncio.get_event_loop()

        self.event: Dict[str, List[Callable]] = {}

    async def message_handler(self, app, message: dict, context: dict) -> None:
        """
        调用支持处理器

        :param app:         主程序
        :param message:     消息
        :param context:     上下文
        :return:
        """
        # 消息处理后关闭列表，双向队列
        param_close = deque()
        try:
            for handler in self.handlers:
                is_continue = False
                for f in handler.filters:
                    if f not in self.method_async_state:
                        self.method_async_state[f.support] = iscoroutinefunction(f.support)
                    if self.method_async_state[f.support]:
                        if not await f.support(app, message, context):
                            is_continue = True
                            break
                    else:
                        if not await self.loop.run_in_executor(None, f.support, app, message, context):
                            is_continue = True
                            break
                if is_continue:
                    continue
                param_value = []
                for param in self.method_parameters[handler.func]:
                    if not await parameter_resolver.support_resolver(param, message, context):
                        break
                    param_value.append(await parameter_resolver.resolver(param, app, message, context))
                    param_close.append(param)
                else:
                    if self.method_async_state[handler.func]:
                        await handler.func(*param_value)
                    else:
                        await self.loop.run_in_executor(None, handler.func, *param_value)
                    if handler.first_over:
                        return
        except Exception as e:
            for param in param_close:
                await parameter_resolver.close(param, context)
            logger.exception(e)

    def register_handler(
            self,
            fn: Callable,
            order: int = 0,
            first_over: bool = False,
            filters: List[Filter] = None,
            nullable: bool = True,
            skipnull: bool = True
    ):
        """
        创建消息处理器
        :param fn           回调函数
        :param order:       优先级
        :param first_over:  首次匹配则结束, True: 触发第一次后就跳过
        :param filters:     过滤器
        :param nullable:    参数解析遇到None(解析失败, 没有返回结果)是否抛出错误
        :param skipnull:    如果参数解析结果为空值(解析失败，没有返回结果), True跳过函数调用, False继续调用(失败参数会传入None)
        :return:
        """
        self.method_parameters[fn] = parameter_resolver.support_function(fn)
        self.method_async_state[fn] = iscoroutinefunction(fn)
        for filter_ in filters:
            self.method_async_state[filter_.support] = iscoroutinefunction(filter_.support)
        self.handlers.append(Config(fn, filters, order, first_over, nullable, skipnull))
        self.handlers.sort(key=lambda x: x.order)

    def register_crontab(self, cron: str, fn: Callable, app):
        """
        创建定时任务
        :param fn:      任务函数
        :param cron:    定时表达式
        :param app:     主程序
        :return:
        """

        async def task():
            # 未连接状态不执行定时任务
            if not app.connect_state:
                return
            param_close = deque()
            param_value = deque()
            try:
                for param in parameters:
                    if not await parameter_resolver.support_resolver(param, {}, {}):
                        raise ParameterError('定时任务参数解析错误', fn, param)
                    param_value.append(await parameter_resolver.resolver(param, app, {}, {}))
                    param_close.append(param)
                else:
                    if async_state:
                        await fn(*param_value)
                    else:
                        await self.loop.run_in_executor(None, fn, *param_value)
            except Exception as e:
                logger.exception(e)
            for param in param_close:
                try:
                    await parameter_resolver.close(param, {})
                except Exception as e:
                    logger.exception(e)
        parameters = parameter_resolver.support_function(fn)
        async_state = iscoroutinefunction(fn)
        aiocron.crontab(cron, task)

    def register_event(self, fn: Callable, event: str):
        """
        注册事件
        :param fn:      方法
        :param event:   事件
        :return:
        """
        self.method_parameters[fn] = parameter_resolver.support_function(fn)
        self.method_async_state[fn] = iscoroutinefunction(fn)
        self.event.setdefault(event, []).append(fn)

    async def execute_event_task(self, event: str, app):
        if event not in self.event:
            return
        param_close = deque()
        for fn in self.event[event]:
            param_value = deque()
            for param in self.method_parameters[fn]:
                param_value.append(await parameter_resolver.resolver(param, app, {}, {}))
            try:
                if self.method_async_state[fn]:
                    await fn(*param_value)
                else:
                    fn(*param_value)
            except Exception as err:
                logger.exception(err)
        for param in param_close:
            try:
                await parameter_resolver.close(param, {})
            except Exception as err:
                logger.exception(err)
