from onebot import OneBot
from onebot.parameter import GetAPP, GetGroupID, GetJSON, GetSendUserID

onebot = OneBot(host='127.0.0.1', port=3001, token='123123')


@onebot.listener()
async def group(
        app: OneBot = GetAPP(),
        group_id: int = GetGroupID(),
        send_user_id: int = GetSendUserID(),
        json: dict = GetJSON()
):
    print(json)


if __name__ == '__main__':
    onebot.run()
