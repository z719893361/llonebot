from onebot.fliters import Filter


class FriendMessage(Filter):
    """
    过滤好友消息
    """
    async def support(self, context: dict, state: dict) -> bool:
        message = context['request']
        return 'group_id' not in message and 'user_id' in message
