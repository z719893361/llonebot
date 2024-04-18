# llonebot

适配LiteLoaderQQNT插件

### 安装

使用以下命令安装项目：

```bash
pip install llonebot
```

### 使用示例
```python
from onebot import OneBot
from onebot.types import MessageBuilder
from onebot.parameter.arguments import GetGroupID, GetJSON, GetMessageID

onebot = OneBot(host='localhost', port=3001, token='123')

@onebot.listener(filters=[])
async def group(app: OneBot, group_id: int = GetGroupID(), message_id: int = GetMessageID(), data: dict = GetJSON()):
    await app.send_group_msg(group_id, "测试")
    await app.send_group_msg(group_id, MessageBuilder().reply(message_id).text("测试"))


if __name__ == "__main__":
    onebot.run()
```


