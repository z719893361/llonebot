from loguru import logger
from onebot.events.interfaces import EventHandler


class RequestEventHandler(EventHandler):

    async def support(self, context: dict, state: dict) -> bool:
        return context['request'].get('post_type') == 'request'

    async def handler(self, context: dict, state: dict):
        message = context['request']
        request_type = message.get('request_type')
        if request_type == 'friend':
            logger.info(
                '好友请求 - QQ号: {}',
                message['user_id']
            )
        elif request_type == 'group':
            sub_type = message.get('sub_type')
            if sub_type == 'add':
                logger.info(
                    '加群请求 - 群号: {} QQ号: {} 验证信息: {}',
                    message['group_id'],
                    message['user_id'],
                    message['comment']
                )
            elif sub_type == 'invite':
                logger.info(
                    '邀请入群 - 群号: {}',
                    message['group_id']
                )
        app = state['app']
        await app.event_manager.message_handler(app, message, context)
