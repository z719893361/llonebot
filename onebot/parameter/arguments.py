import asyncio
import json
from inspect import Parameter, isasyncgenfunction, isgeneratorfunction, iscoroutinefunction
from typing import Any, Optional, Set, List

from onebot.parameter.interfaces import Dependency
from onebot.types import Sender, Image, Record, File, FriendAddRequest, GroupInviteRequest


class GetAPP(Dependency):
    """
    获取主程序
    """

    async def support(self, parameter: Parameter, scope: dict) -> bool:
        return True

    async def resolve(self, parameter: Parameter, scope: dict):
        return scope['app']


class GetMessageID(Dependency):
    """
    从消息中取JSON
    """

    async def support(self, parameter: Parameter, scope: dict) -> bool:
        return 'request' in scope and 'message_id' in scope['request']

    async def resolve(self, parameter: Parameter, scope: dict) -> Optional[int]:
        return scope['request'].get('message_id')


class GetGroupID(Dependency):
    """
    获取群组ID
    """

    def __init__(self, allow_null: bool = False):
        self.allow_null = allow_null

    async def support(self, parameter: Parameter, scope: dict) -> bool:
        if self.allow_null:
            return True
        return 'request' in scope and 'group_id' in scope['request']

    async def resolve(self, parameter: Parameter, scope: dict) -> Optional[int]:
        return scope.get('request', {}).get('group_id')


class GetUserID(Dependency):
    """
    获取发送用户QQ
    """

    async def support(self, parameter: Parameter, scope: dict) -> bool:
        return 'request' in scope and 'user_id' in scope['request']

    async def resolve(self, parameter: Parameter, scope: dict) -> Optional[int]:
        return scope['request'].get('user_id')


class GetRobotID(Dependency):
    """
    获取发送用户QQ
    """

    async def support(self, parameter: Parameter, scope: dict) -> bool:
        return 'request' in scope and 'self_id' in scope['request']

    async def resolve(self, parameter: Parameter, scope: dict) -> Optional[int]:
        return scope['request']['self_id']


class GetSender(Dependency):
    """
    获取发送人信息
    """

    async def support(self, parameter: Parameter, scope: dict) -> bool:
        return 'request' in scope and 'sender' in scope['request']

    async def resolve(self, parameter: Parameter, scope: dict) -> Optional[Sender]:
        if 'sender' in scope:
            return scope['sender']
        scope['sender'] = Sender.model_validate(scope['request']['sender'])
        return scope['sender']


class GetQuote(Dependency):
    """
    获取消息引用ID
    """

    async def support(self, parameter: Parameter, scope: dict) -> bool:
        return 'request' in scope and 'reply' in scope['request']

    async def resolve(self, parameter: Parameter, scope: dict) -> Any:
        return scope['context'].get('reply')


class GetMessageChain(Dependency):
    """
    获取模型解析后的消息
    """

    async def support(self, parameter: Parameter, scope: dict) -> bool:
        return 'message_chain' in scope

    async def resolve(self, parameter: Parameter, scope: dict) -> list:
        return scope.get('message_chain')


class GetAt(Dependency):
    """
    获取at
    """

    async def support(self, parameter: Parameter, scope: dict) -> bool:
        return 'at' in scope

    async def resolve(self, parameter: Parameter, scope: dict) -> Set[str]:
        return scope.get('at')


class GetText(Dependency):
    """
    获取文本
    """

    def __init__(self, joint: bool = True, delimiter=''):
        self.joint = joint
        self.delimiter = delimiter

    async def support(self, parameter: Parameter, scope: dict) -> bool:
        return 'text' in scope

    async def resolve(self, parameter: Parameter, scope: dict) -> List[str] | str | None:
        if self.joint:
            return self.delimiter.join(scope['text'])
        else:
            return scope['text']


class GetJSON(Dependency):
    """
    获取JSON
    """

    def __init__(self, raw=False):
        self.raw = raw

    async def support(self, parameter: Parameter, scope: dict) -> bool:
        return 'json' in scope

    async def resolve(self, parameter: Parameter, scope: dict) -> Optional[dict]:
        if self.raw:
            return scope['json']
        else:
            return json.loads(scope['json'])


class GetImage(Dependency):
    """
    获取图片
    """

    async def support(self, parameter: Parameter, scope: dict) -> bool:
        return 'image' in scope

    async def resolve(self, parameter: Parameter, scope: dict) -> Optional[List[Image]]:
        return scope['image']


class GetFace(Dependency):
    """
    获取表情
    """

    async def support(self, parameter: Parameter, scope: dict) -> bool:
        return 'face' in scope

    async def resolve(self, parameter: Parameter, scope: dict) -> List[int]:
        return scope['face']


class GetRecord(Dependency):
    """
    获取语音
    """

    async def support(self, parameter: Parameter, scope: dict) -> bool:
        return 'record' in scope

    async def resolve(self, parameter: Parameter, scope: dict) -> Record:
        return scope['record']


class GetFile(Dependency):
    """
    获取文件
    """

    async def support(self, parameter: Parameter, scope: dict) -> bool:
        return 'file' in scope

    async def resolve(self, parameter: Parameter, scope: dict) -> File:
        return scope['file']


class GetFriendAddRequest(Dependency):
    """
    好友请求
    """

    async def support(self, parameter: Parameter, scope: dict) -> bool:
        return 'request' in scope and scope['request'].get('request_type') == 'friend'

    async def resolve(self, parameter: Parameter, scope: dict) -> FriendAddRequest:
        return FriendAddRequest.model_validate(scope['request'])


class GetGroupInviteRequest(Dependency):
    """
    邀请进群
    """

    async def support(self, parameter: Parameter, scope: dict) -> bool:
        return (
                'request' in scope and
                scope['request'].get('post_type') == 'request' and
                scope['request'].get('request_type') == 'group' and
                scope['request'].get('sub_type') == 'invite'
        )

    async def resolve(self, parameter: Parameter, scope: dict) -> GroupInviteRequest:
        return GroupInviteRequest.model_validate(scope['request'])


class Depends(Dependency):
    def __init__(self, func, use_cache=True, args=None, kwargs=None):
        # 方法
        if kwargs is None:
            kwargs = {}
        if args is None:
            args = ()
        self.func = func
        self.args = args
        self.kwargs = kwargs
        # 是否使用缓存
        self.use_cache = use_cache
        # 异步生成器
        self.is_asyncgen = isasyncgenfunction(func)
        # 同步生成器
        self.is_generator = isgeneratorfunction(func)
        # 异步函数
        self.is_async_func = iscoroutinefunction(func)
        # 计算哈希
        items_tuple = tuple(sorted(kwargs.items()))
        # 结果哈希标识
        self.cache_key = hash((self.func, self.args, items_tuple))
        # 生成器哈希标识
        self.generator_key = hash((self.func, self.args, items_tuple, 'generator'))

    async def support(self, parameter: Parameter, scpe: dict) -> bool:
        return True

    async def resolve(self, parameter: Parameter, scope: dict) -> Any:
        if self.use_cache and self.cache_key in scope:
            return scope[self.cache_key]
        if self.is_generator:
            generator = self.func(*self.args, **self.kwargs)
            scope[self.generator_key] = generator
            result = await asyncio.to_thread(next, generator)
        elif self.is_asyncgen:
            generator = self.func(*self.args, **self.kwargs)
            scope[self.generator_key] = generator
            result = await anext(generator)
        elif self.is_async_func:
            result = await self.func(*self.args, **self.kwargs)
        else:
            result = await asyncio.to_thread(self.func, *self.args, *self.kwargs)
        if self.use_cache:
            scope[self.cache_key] = result
        return result

    async def close(self, parameter: Parameter, scope: dict, exc: Exception):
        # 生成器是否存在
        if self.generator_key not in scope:
            return
        generator = scope[self.generator_key]
        if self.is_generator:
            if exc is not None:
                try:
                    generator.throw(exc)
                except StopIteration:
                    pass
            else:
                try:
                    next(generator)
                except StopIteration:
                    pass
        elif self.is_asyncgen:
            if exc is not None:
                try:
                    await generator.athrow(exc)
                except StopAsyncIteration:
                    pass
            else:
                try:
                    await anext(generator)
                except StopAsyncIteration:
                    pass
