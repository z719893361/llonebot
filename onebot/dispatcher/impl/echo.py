from onebot.dispatcher.interfaces import EventDispatcher


class EchoEventHandler(EventDispatcher):
    async def support(self, scope: dict) -> bool:
        return 'echo' in scope['request']

    async def handle(self, scope: dict):
        app = scope['app']
        app.set_response(scope['request']['echo'], scope['request'])
