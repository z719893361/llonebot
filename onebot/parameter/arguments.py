from __future__ import annotations

import asyncio
from inspect import Parameter, isgeneratorfunction, isasyncgenfunction, iscoroutinefunction
from typing import Union, Optional, List, Set, Any, TYPE_CHECKING

from onebot.dtypes.models import Record, File, Image, Sender, FriendAddRequest, GroupInviteRequest
from onebot.parameter.interfaces import Depend

if TYPE_CHECKING:
    from onebot.application import OneBot


class GetAPP(Depend):
    """
    获取主程序
    """

    async def support(self, message: dict, context: dict) -> bool:
        return True

    async def resolver(self, parameter: Parameter, app, message: dict, context: dict) -> OneBot:
        return app


class GetMessageID(Depend):
    """
    从消息中取JSON
    """

    async def support(self, message: dict, context: dict) -> bool:
        return 'message_id' in message

    async def resolver(self, parameter: Parameter, app, message: dict, context: dict) -> Optional[int]:
        return message.get('message_id')


class GetGroupID(Depend):
    """
    获取群组ID
    """

    async def support(self, message: dict, context: dict) -> bool:
        return 'group_id' in message

    async def resolver(self, parameter: Parameter, app, message: dict, context: dict) -> Optional[int]:
        return message.get('group_id')


class GetSendUserID(Depend):
    """
    获取发送用户QQ
    """

    async def support(self, message: dict, context: dict) -> bool:
        return 'user_id' in message

    async def resolver(self, parameter: Parameter, app, message: dict, context: dict) -> Optional[int]:
        return message.get('user_id')


class GetRobotID(Depend):
    """
    获取发送用户QQ
    """

    async def support(self, message: dict, context: dict) -> bool:
        return 'self_id' in message

    async def resolver(self, parameter: Parameter, app, message: dict, context: dict) -> Optional[int]:
        return message.get('self_id')


class GetSender(Depend):
    """
    获取发送人信息
    """

    async def support(self, message: dict, context: dict) -> bool:
        return 'sender' in message

    async def resolver(self, parameter: Parameter, app, message: dict, context: dict) -> Optional[Sender]:
        if 'sender' in context:
            return context['sender']
        context['sender'] = Sender.model_validate(message['sender'])
        return context['sender']


class GetQuote(Depend):
    """
    获取消息引用ID
    """

    async def support(self, message: dict, context: dict) -> bool:
        return 'reply' in message

    async def resolver(self, parameter: Parameter, app, message: dict, context: dict) -> Any:
        return context.get('reply')


class GetMessageChain(Depend):
    """
    获取模型解析后的消息
    """

    async def support(self, message: dict, context: dict) -> bool:
        return 'message' in context

    async def resolver(self, parameter: Parameter, app, message: dict, context: dict) -> list:
        return context.get('message')


class GetRawMessageChain(Depend):
    """
    获取Json格式原始消息
    """

    async def support(self, message: dict, context: dict) -> bool:
        return 'raw_message' in message

    async def resolver(self, parameter: Parameter, app, message: dict, context: dict) -> str:
        return message.get('raw_message')


class GetMessage(Depend):
    """
    获取原始报文
    """

    async def support(self, message: dict, context: dict) -> bool:
        return True

    async def resolver(self, parameter: Parameter, app, message: dict, context: dict) -> dict:
        return message


class GetAt(Depend):
    """
    获取at
    """

    async def support(self, message: dict, context: dict) -> bool:
        return 'at' in context

    async def resolver(self, parameter: Parameter, app, message: dict, context: dict) -> Set[str]:
        return context.get('at')


class GetText(Depend):
    """
    获取文本
    """

    def __init__(self, concat: bool = True, delimiter=''):
        self.concat = concat
        self.delimiter = delimiter

    async def support(self, message: dict, context: dict) -> bool:
        return 'text' in context

    async def resolver(self, parameter: Parameter, app, message: dict, context: dict) -> Union[List[str], str, None]:
        if 'text' not in context:
            return
        if self.concat:
            return self.delimiter.join(context['text'])
        else:
            return context['text']


class GetJSON(Depend):
    """
    获取JSON
    """

    async def support(self, message: dict, context: dict) -> bool:
        return 'json' in context

    async def resolver(self, parameter: Parameter, app, message: dict, context: dict) -> Optional[dict]:
        return context.get('json')


class GetImage(Depend):
    """
    获取图片
    """

    async def support(self, message: dict, context: dict) -> bool:
        return 'image' in context

    async def resolver(self, parameter: Parameter, app, message: dict, context: dict) -> Optional[List[Image]]:
        return context.get('image')


class GetFace(Depend):
    """
    获取表情
    """

    async def support(self, message: dict, context: dict) -> bool:
        return 'face' in context

    async def resolver(self, parameter: Parameter, app, message: dict, context: dict) -> List[int]:
        return context.get('face')


class GetRecord(Depend):
    """
    获取语音
    """

    async def support(self, message: dict, context: dict) -> bool:
        return 'record' in context

    async def resolver(self, parameter: Parameter, app, message: dict, context: dict) -> Record:
        return context.get('record')


class GetFile(Depend):
    """
    获取文件
    """

    async def support(self, message: dict, context: dict) -> bool:
        return 'file' in context

    async def resolver(self, parameter: Parameter, app, message: dict, context: dict) -> File:
        return context.get('file')


class GetFriendAddRequest(Depend):
    """
    好友请求
    """

    async def support(self, message: dict, context: dict) -> bool:
        return message.get('request_type') == 'friend'

    async def resolver(self, parameter: Parameter, app, message: dict, context: dict) -> FriendAddRequest:
        return FriendAddRequest.model_validate(message)


class GetGroupInviteRequest(Depend):
    """
    邀请进群
    """

    async def support(self, message: dict, context: dict) -> bool:
        return (
                message.get('post_type') == 'request' and
                message.get('request_type') == 'group' and
                message.get('sub_type') == 'invite'
        )

    async def resolver(self, parameter: Parameter, app, message: dict, context: dict) -> GroupInviteRequest:
        return GroupInviteRequest.model_validate(message)


class GetContext(Depend):
    """
    邀请进群
    """

    async def support(self, message: dict, context: dict) -> bool:
        return True

    async def resolver(self, parameter: Parameter, app, message: dict, context: dict) -> dict:
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

    async def support(self, message: dict, context: dict) -> bool:
        return True

    async def resolver(self, parameter: Parameter, app, message: dict, context: dict) -> Any:
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

    async def close(self, parameter: Parameter, context: dict):
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
