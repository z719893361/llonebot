from typing import Union

from onebot.filter.interfaces import FilterInterface


class Command(FilterInterface):
    def __init__(self, command: str):
        self._command = command

    async def support(self, scope: dict):
        return scope['full_text'] == self._command
