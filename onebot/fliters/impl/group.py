from __future__ import annotations
from typing import Set, List, Union

from onebot.fliters.interfaces import Filter


class GroupMessage(Filter):
    """
    是否为群组消息
    """

    async def support(self, context: dict, state: dict) -> bool:
        return 'group_id' in context['request']


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

    async def support(self, context: dict, state: dict):
        return context['request'].get('group_id') in self.numbers


class AtMe(Filter):
    """
    是否@机器人
    """
    async def support(self, context: dict, state: dict) -> bool:
        if 'at_me' not in context:
            context['at_me'] = 'at' in context and str(context['request'].get('self_id')) in context['at']
        return context['at_me']
