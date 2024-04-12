from __future__ import annotations
from typing import Set, List, Union

from onebot.fliters.interfaces import Filter


class Group(Filter):
    """
    是否为群组消息
    """

    async def support(self, app, message: dict, context: dict) -> bool:
        return 'group_id' in message


class GroupNumber(Filter):
    """
    群号过滤
    """

    def __init__(self, numbers: Union[Set[int], List[int], int]):
        if isinstance(numbers, list):
            self.numbers = set(numbers)
        elif isinstance(numbers, set):
            self.numbers = numbers
        elif isinstance(numbers, int):
            self.numbers = {numbers}
        else:
            raise ValueError('类型错误')

    async def support(self, app, message: dict, context: dict):
        return message.get('group_id') in self.numbers


class AtMe(Filter):
    """
    是否@机器人
    """
    async def support(self, app, message: dict, context: dict) -> bool:
        if 'at_me' not in context:
            context['at_me'] = 'at' in context and str(message.get('self_id')) in context['at']
        return context['at_me']
