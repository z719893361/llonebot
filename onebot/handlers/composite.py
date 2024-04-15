from __future__ import annotations

from typing import List

from .impl.request import RequestEventHandler
from .interfaces import EventHandler
from .impl.echo import EchoEventHandler
from .impl.message import MessageEventHandler


class EventComposite(EventHandler):
    """
    消息处理器组合器
    """
    def __init__(self):
        self._handlers: List[EventHandler] = []

    async def support(self, context: dict, state: dict):
        pass

    async def handler(self, context: dict, state: dict):
        for handler in self._handlers:
            if await handler.support(context, state):
                await handler.handler(context, state)
                return

    def add_handler(self, handler: EventHandler):
        self._handlers.append(handler)


event_dispatcher = EventComposite()
event_dispatcher.add_handler(EchoEventHandler())
event_dispatcher.add_handler(MessageEventHandler())
event_dispatcher.add_handler(RequestEventHandler())
