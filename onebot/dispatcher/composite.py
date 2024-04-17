from typing import List

from onebot.dispatcher.impl.echo import EchoEventHandler
from onebot.dispatcher.impl.message import MessageEventHandler
from onebot.dispatcher.impl.request import RequestEvent
from onebot.dispatcher.interfaces import EventDispatcher


class EventComposite:
    """
    消息处理器组合器
    """

    def __init__(self):
        self.dispatchers: List[EventDispatcher] = []

    async def support(self, scope: dict) -> bool:
        pass

    async def handler(self, scope: dict):
        for handler in self.dispatchers:
            if await handler.support(scope):
                await handler.handle(scope)
                return

    def add_handler(self, handler: EventDispatcher):
        self.dispatchers.append(handler)


dispatcher = EventComposite()
dispatcher.add_handler(MessageEventHandler())
dispatcher.add_handler(EchoEventHandler())
dispatcher.add_handler(RequestEvent())
