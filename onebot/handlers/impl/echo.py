"""
消息应答
"""
from __future__ import annotations

from onebot.handlers.interfaces import EventHandler


class EchoEventHandler(EventHandler):
    async def support(self, context: dict, state: dict) -> bool:
        return 'echo' in context['request']

    async def handler(self, context: dict, state: dict):
        app = state['app']
        app.set_response(context['request']['echo'], context['request'])
