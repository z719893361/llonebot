from onebot.fliters import Filter


class FriendMessage(Filter):
    """
    过滤好友消息
    """
    async def support(self, app, message: dict, context: dict) -> bool:
        return 'group_id' not in message and 'user_id' in message
