from onebot.events.interfaces import EventHandler


class MetaEventEventHandler(EventHandler):

    async def support(self, context: dict, state: dict) -> bool:
        return context['request'].get('post_type') == 'meta_event'

    async def handler(self, context: dict, state: dict):
        app = state['app']
        app.robot_id = context['request']['self_id']
