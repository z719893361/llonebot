"""
消息应答
"""
from __future__ import annotations

from onebot.handlers.interfaces import EventHandler


class EchoEventHandler(EventHandler):
    async def support(self, app, message: dict, context: dict) -> bool:
        return 'echo' in message

    async def handler(self, app, message: dict, context: dict):
        app.set_response(message['echo'], message)
