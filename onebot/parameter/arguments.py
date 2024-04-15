from __future__ import annotations

import asyncio
import json
from inspect import Parameter, isgeneratorfunction, isasyncgenfunction, iscoroutinefunction
from typing import Union, Optional, List, Set, Any, TYPE_CHECKING

from onebot.dtypes.models import Record, File, Image, Sender, FriendAddRequest, GroupInviteRequest
from onebot.parameter.interfaces import Depend


class GetAPP(Depend):
    """
    获取主程序
    """

    async def support(self, context: dict, state: dict) -> bool:
        return True

    async def resolver(self, parameter: Parameter, context: dict, state: dict):
        return state['app']


class GetMessageID(Depend):
    """
    从消息中取JSON
    """

    async def support(self, context: dict, state: dict) -> bool:
        return 'message_id' in context['request']

    async def resolver(self, parameter: Parameter, context: dict, state: dict) -> Optional[int]:
        return context['request'].get('message_id')


class GetGroupID(Depend):
    """
    获取群组ID
    """

    def __init__(self, allow_none: bool = False):
        self.allow_none = allow_none

    async def support(self, context: dict, state: dict) -> bool:
        if self.allow_none:
            return True
        return 'group_id' in context['request']

    async def resolver(self, parameter: Parameter, context: dict, state: dict) -> Optional[int]:
        return context['request'].get('group_id')


class GetUserID(Depend):
    """
    获取发送用户QQ
    """

    async def support(self, context: dict, state: dict) -> bool:
        return 'user_id' in context['request']

    async def resolver(self, parameter: Parameter, context: dict, state: dict) -> Optional[int]:
        return context['request'].get('user_id')


class GetRobotID(Depend):
    """
    获取发送用户QQ
    """

    async def support(self, context: dict, state: dict) -> bool:
        return 'self_id' in context['request']

    async def resolver(self, parameter: Parameter, context: dict, state: dict) -> Optional[int]:
        return context['request'].get('self_id')


class GetSender(Depend):
    """
    获取发送人信息
    """

    async def support(self, context: dict, state: dict) -> bool:
        return 'sender' in context['request']

    async def resolver(self, parameter: Parameter, context: dict, state: dict) -> Optional[Sender]:
        if 'sender' in context:
            return context['sender']
        context['sender'] = Sender.model_validate(context['request']['sender'])
        return context['sender']


class GetQuote(Depend):
    """
    获取消息引用ID
    """

    async def support(self, context: dict, state: dict) -> bool:
        return 'reply' in context['request']

    async def resolver(self, parameter: Parameter, context: dict, state: dict) -> Any:
        return context.get('reply')


class GetMessageChain(Depend):
    """
    获取模型解析后的消息
    """

    async def support(self, context: dict, state: dict) -> bool:
        return 'message' in context

    async def resolver(self, parameter: Parameter, context: dict, state: dict) -> list:
        return context.get('message')


class GetRawMessageChain(Depend):
    """
    获取Json格式原始消息
    """

    async def support(self, context: dict, state: dict) -> bool:
        return 'raw_message' in context['request']

    async def resolver(self, parameter: Parameter, context: dict, state: dict) -> str:
        return context['request'].get('raw_message')


class GetMessage(Depend):
    """
    获取原始报文
    """

    async def support(self, context: dict, state: dict) -> bool:
        return True

    async def resolver(self, parameter: Parameter, context: dict, state: dict) -> dict:
        return context['request']


class GetAt(Depend):
    """
    获取at
    """

    async def support(self, context: dict, state: dict) -> bool:
        return 'at' in context

    async def resolver(self, parameter: Parameter, context: dict, state: dict) -> Set[str]:
        return context.get('at')


class GetText(Depend):
    """
    获取文本
    """

    def __init__(self, concat: bool = True, delimiter=''):
        self.concat = concat
        self.delimiter = delimiter

    async def support(self, context: dict, state: dict) -> bool:
        return 'text' in context

    async def resolver(self, parameter: Parameter, context: dict, state: dict) -> Union[List[str], str, None]:
        if self.concat:
            return self.delimiter.join(context['text'])
        else:
            return context['text']


class GetJSON(Depend):
    """
    获取JSON
    """

    def __init__(self, text=False):
        self.text = text

    async def support(self, context: dict, state: dict) -> bool:
        return 'json' in context

    async def resolver(self, parameter: Parameter, context: dict, state: dict) -> Optional[dict]:
        if self.text:
            return context.get('json')
        else:
            return json.loads(context.get('json'))


class GetImage(Depend):
    """
    获取图片
    """

    async def support(self, context: dict, state: dict) -> bool:
        return 'image' in context

    async def resolver(self, parameter: Parameter, context: dict, state: dict) -> Optional[List[Image]]:
        return context.get('image')


class GetFace(Depend):
    """
    获取表情
    """

    async def support(self, context: dict, state: dict) -> bool:
        return 'face' in context

    async def resolver(self, parameter: Parameter, context: dict, state: dict) -> List[int]:
        return context.get('face')


class GetRecord(Depend):
    """
    获取语音
    """

    async def support(self, context: dict, state: dict) -> bool:
        return 'record' in context

    async def resolver(self, parameter: Parameter, context: dict, state: dict) -> Record:
        return context.get('record')


class GetFile(Depend):
    """
    获取文件
    """

    async def support(self, context: dict, state: dict) -> bool:
        return 'file' in context

    async def resolver(self, parameter: Parameter, context: dict, state: dict) -> File:
        return context.get('file')


class GetFriendAddRequest(Depend):
    """
    好友请求
    """

    async def support(self, context: dict, state: dict) -> bool:
        return context['request'].get('request_type') == 'friend'

    async def resolver(self, parameter: Parameter, context: dict, state: dict) -> FriendAddRequest:
        return FriendAddRequest.model_validate(context['request'])


class GetGroupInviteRequest(Depend):
    """
    邀请进群
    """

    async def support(self, context: dict, state: dict) -> bool:
        return (
                context['request'].get('post_type') == 'request' and
                context['request'].get('request_type') == 'group' and
                context['request'].get('sub_type') == 'invite'
        )

    async def resolver(self, parameter: Parameter, context: dict, state: dict) -> GroupInviteRequest:
        return GroupInviteRequest.model_validate(context['request'])


class GetContext(Depend):
    """
    邀请进群
    """

    async def support(self, context: dict, state: dict) -> bool:
        return True

    async def resolver(self, parameter: Parameter, context: dict, state: dict) -> dict:
        return context


class Depends(Depend):
    def __init__(self, fn, use_cache=True, args=None, kwargs=None):
        # 方法
        if kwargs is None:
            kwargs = {}
        if args is None:
            args = ()
        # 函数
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        # 是否使用缓存
        self.use_cache = use_cache
        # 异步生成器
        self.is_asyncgen_func = isasyncgenfunction(fn)
        # 同步生成器
        self.is_generator_fn = isgeneratorfunction(fn)
        # 异步函数
        self.is_async_fn = iscoroutinefunction(fn)
        # 计算哈希
        items_tuple = tuple(sorted(kwargs.items()))
        # 结果哈希标识
        self.cache_hash = hash((self.fn, self.args, items_tuple))
        # 生成器哈希标识
        self.generator_hash = hash((self.fn, self.args, items_tuple, 'generator'))

    async def support(self, context: dict, state: dict) -> bool:
        return True

    async def resolver(self, parameter: Parameter, context: dict, state: dict) -> Any:
        if self.use_cache and self.cache_hash in context:
            return context[self.cache_hash]
        if self.is_generator_fn:
            generator = self.fn(*self.args, **self.kwargs)
            context[self.generator_hash] = generator
            result = await asyncio.to_thread(next, generator)
        elif self.is_asyncgen_func:
            generator = self.fn(*self.args, **self.kwargs)
            context[self.generator_hash] = generator
            result = await anext(generator)
        elif self.is_async_fn:
            result = await self.fn(*self.args, **self.kwargs)
        else:
            result = await asyncio.to_thread(self.fn, *self.args, *self.kwargs)
        if self.use_cache:
            context[self.cache_hash] = result
        return result

    async def close(self, parameter: Parameter, context: dict, state: dict):
        if self.generator_hash not in context:
            return
        generator = context[self.generator_hash]
        if self.is_generator_fn:
            try:
                while True:
                    next(generator)
            except StopIteration:
                pass
        elif self.is_asyncgen_func:
            try:
                while True:
                    await anext(generator)
            except StopAsyncIteration:
                pass
