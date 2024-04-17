from loguru import logger

from onebot.dispatcher.interfaces import EventDispatcher


class RequestEvent(EventDispatcher):
    async def support(self, scope: dict):
        return scope['request'].get('post_type') == 'request'

    async def handle(self, scope: dict):
        request = scope.get('request')
        request_type = request.get('request_type')
        if request_type == 'friend':
            logger.info('好友请求 - QQ号: {user_id}', **request)
        elif request_type == 'group':
            sub_type = request.get('sub_type')
            if sub_type == 'add':
                logger.info('加群请求 - 群号: {group_id} QQ号: {user_id} 验证信息: {comment}', **request)
            elif sub_type == 'invite':
                logger.info('邀请入群 - 群号: {group_id}', **request)
        router = scope['router']
        return await router(scope)
