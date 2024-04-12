from __future__ import annotations

import asyncio
from collections import deque
from dataclasses import dataclass
from inspect import signature, getfile, iscoroutinefunction, Parameter
from typing import Callable, List, Dict, ValuesView

from loguru import logger

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


class HandlerRegister:

    def __init__(self):
        self.handlers: List[Config] = []
        # 方法参数缓存
        self.method_parameters: Dict[Callable, ValuesView[Parameter]] = {}
        # 异步函数缓存
        self.method_async_status: Dict[Callable, bool] = {}

        self.loop = asyncio.get_event_loop()

    def register(
            self,
            fn: Callable,
            order: int = 0,
            first_over: bool = False,
            filters: List[Filter] = None,
            nullable: bool = True,
            skipnull: bool = True
    ):
        """
        注册处理器
        :param fn           回调函数
        :param order:       优先级
        :param first_over:  首次匹配则结束, True: 触发第一次后就跳过
        :param filters:     过滤器
        :param nullable:    参数解析遇到None(解析失败, 没有返回结果)是否抛出错误
        :param skipnull:    如果参数解析结果为空值(解析失败，没有返回结果), True跳过函数调用, False继续调用(失败参数会传入None)
        :return:
        """
        arguments = signature(fn).parameters.values()
        for param in arguments:
            if not parameter_resolver.support_parameter(param):
                file_path = getfile(fn)
                method_name = fn.__name__
                error_message = f"Hit: {param.name}"
                if param.annotation != param.empty:
                    error_message += f":{param.annotation}"
                if param.default != param.empty:
                    error_message += f" = {param.default})"
                error_message += f" 参数不支持解析, 文件路径: {file_path}, 方法名: {method_name}"
                raise TypeError(error_message)
        # 预处理函数，减少后续判断
        self.method_parameters[fn] = signature(fn).parameters.values()
        self.method_async_status[fn] = iscoroutinefunction(fn)
        for filter_ in filters:
            self.method_async_status[filter_.support] = iscoroutinefunction(filter_.support)
        # 添加过滤器并排序
        self.handlers.append(Config(fn, filters, order, first_over, nullable, skipnull))
        self.handlers.sort(key=lambda x: x.order)

    async def handler(self, app, message: dict, context: dict) -> None:
        """
        调用支持处理器

        :param app:         主程序
        :param message:     消息
        :param context:     上下文
        :return:
        """
        # 消息处理后关闭列表，双向队列
        after_close_deque = deque()
        try:
            for handler in self.handlers:
                is_continue = False
                for f in handler.filters:
                    if f not in self.method_async_status:
                        self.method_async_status[f.support] = iscoroutinefunction(f.support)
                    if self.method_async_status[f.support]:
                        if not await f.support(app, message, context):
                            is_continue = True
                            break
                    else:
                        if not await self.loop.run_in_executor(None, f.support, app, message, context):
                            is_continue = True
                            break
                if is_continue:
                    continue
                resolved_params = []
                for param in self.method_parameters[handler.func]:
                    if not await parameter_resolver.support_resolver(param, message, context):
                        break
                    resolved_params.append(await parameter_resolver.resolver(param, app, message, context))
                    after_close_deque.append(param)
                else:
                    if self.method_async_status[handler.func]:
                        await handler.func(*resolved_params)
                    else:
                        await self.loop.run_in_executor(None, handler.func, *resolved_params)
                    if handler.first_over:
                        return
        except Exception as e:
            for param in after_close_deque:
                await parameter_resolver.close(param, context)
            logger.exception(e)
