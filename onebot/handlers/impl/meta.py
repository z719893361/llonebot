from onebot.handlers.interfaces import EventHandler


class MetaEventEventHandler(EventHandler):

    async def support(self, app, message: dict, context: dict) -> bool:
        return message.get('post_type') == 'meta_event'

    async def handler(self, app, message: dict, context: dict):
        app.robot_id = str(message['self_id'])
