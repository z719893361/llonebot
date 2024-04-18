from typing import Set

from onebot.filter.interfaces import Filter


class At(Filter):
    def __init__(self, numbers: Set[int]):
        self.numbers = numbers

    async def support(self, scope: dict) -> bool:
        if 'at' not in scope:
            return False
        return len(scope['at'] & self.numbers) > 0


class AtMe(Filter):
    async def support(self, scope: dict) -> bool:
        if 'at' not in scope or 'request' not in scope:
            return False
        return str(scope['request']['self_id']) in scope['at']
