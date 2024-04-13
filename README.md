# llonebot

适配LiteLoaderQQNT插件

## 安装

使用以下命令安装项目：

```bash
pip install llonebot
```


## 参数列表
- [GetAPP](#GetAPP)
- [GetMessageID](#GetMessageID)
- [GetGroupID](#GetGroupID)
- [GetSendUserID](#GetSendUserID)
- [GetRobotID](#GetRobotID)
- [GetSender](#GetSender)
- [GetQuote](#GetQuote)
- [GetMessageChain](#GetMessageChain)
- [GetRawMessageChain](#GetRawMessageChain)
- [GetMessage](#GetMessage)
- [GetAt](#GetAt)
- [GetText](#GetText)
- [GetJSON](#GetJSON)
- [GetImage](#GetImage)
- [GetFace](#GetFace)
- [GetRecord](#GetRecord)
- [GetFile](#GetFile)
- [GetFriendAddRequest](#GetFriendAddRequest)
- [GetGroupInviteRequest](#GetGroupInviteRequest)
- [GetContext](#GetContext)
- [Depends](#Depends)

## 示例
```python
from onebot import OneBot
from onebot.dtypes import MessageBuilder
from onebot.parameter.arguments import GetAPP, GetGroupID, GetJSON, GetMessageID

app = OneBot(host='localhost', port=3001, token='xxxxx')

@app.listener(filters=[])
async def group(app: OneBot, group_id: int = GetGroupID(), message_id: int = GetMessageID(), data: dict = GetJSON()):
    await app.send_group_msg(group_id, "测试")
    await app.send_group_msg(group_id, MessageBuilder().reply(message_id).text("测试"))


if __name__ == "__main__":
    app.run()
```
