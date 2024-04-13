# llonebot

适配LiteLoaderQQNT插件

## 安装

使用以下命令安装项目：

```bash
pip install llonebot
```

### 调用参数

### 解析器

#### GetAPP

获取onebot主程序

**参数:**

无

---
##### GetMessageID

获取当前消息ID

**参数**
- 无

**返回**
- `int`： 当前消息ID

---
##### GetGroupID
获取当前消息群号

**参数**
- `message: dict`: 消息字典
- `context: dict`: 上下文字典

**返回**
-   `int`: 群号

---
#### GetSendUserID

获取发送用户QQ

**参数:**
- 无

**返回**
-   `int`: QQ

---
#### GetRobotID

获取发送用户QQ

**参数:**

- 无

**返回**
- `int` 机器人QQ

#### GetSender
获取发送人信息

**参数:**

- `message: dict`: 消息字典
- `context: dict`: 上下文字典

## GetQuote

获取消息引用ID

### 参数:

- `message: dict`: 消息字典
- `context: dict`: 上下文字典

## GetMessageChain

获取模型解析后的消息

### 参数:

- `message: dict`: 消息字典
- `context: dict`: 上下文字典

## GetRawMessageChain

获取Json格式原始消息

### 参数:

- `message: dict`: 消息字典
- `context: dict`: 上下文字典

## GetMessage

获取原始报文

### 参数:

- `message: dict`: 消息字典
- `context: dict`: 上下文字典

## GetAt

获取at

### 参数:

- `message: dict`: 消息字典
- `context: dict`: 上下文字典

## GetText

获取文本

### 参数:

- `concat: bool = True`: 是否连接文本，默认为True
- `delimiter: str = ''`: 连接文本时的分隔符，默认为空字符串

- `message: dict`: 消息字典
- `context: dict`: 上下文字典

## GetJSON

获取JSON

### 参数:

- `text: bool = False`: 是否获取文本形式的JSON，默认为False

- `message: dict`: 消息字典
- `context: dict`: 上下文字典

## GetImage

获取图片

### 参数:

- `message: dict`: 消息字典
- `context: dict`: 上下文字典

## GetFace

获取表情

### 参数:

- `message: dict`: 消息字典
- `context: dict`: 上下文字典

## GetRecord

获取语音

### 参数:

- `message: dict`: 消息字典
- `context: dict`: 上下文字典

## GetFile

获取文件

### 参数:

- `message: dict`: 消息字典
- `context: dict`: 上下文字典

## GetFriendAddRequest

好友请求

### 参数:

- `message: dict`: 消息字典
- `context: dict`: 上下文字典

## GetGroupInviteRequest

邀请进群

### 参数:

- `message: dict`: 消息字典
- `context: dict`: 上下文字典

## GetContext

邀请进群

### 参数:

- `message: dict`: 消息字典
- `context: dict`: 上下文字典

## Depends

### 参数:

- `fn`: 函数
- `use_cache: bool = True`: 是否使用缓存，默认为True
- `args: Optional[tuple] = None`: 函数参数，默认为None
- `kwargs: Optional[dict] = None`: 关键字参数，默认为None

- `message: dict`: 消息字典
- `context: dict`: 上下文字典

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
from onebot.parameter.arguments import GetGroupID, GetJSON, GetMessageID

robot = OneBot(host='localhost', port=3001, token='xxxxx')

@robot.listener(filters=[])
async def group(app: OneBot, group_id: int = GetGroupID(), message_id: int = GetMessageID(), data: dict = GetJSON()):
    await app.send_group_msg(group_id, "测试")
    await app.send_group_msg(group_id, MessageBuilder().reply(message_id).text("测试"))


if __name__ == "__main__":
    robot.run()
```
