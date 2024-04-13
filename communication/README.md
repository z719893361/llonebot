### 参数注入方式

在参数注入中，有两种方式可供选择：注解方式和注入器方式。

### 默认值绑定注入器方式

在注解方式中，你可以直接在方法的参数中使用注解来指定注入的对象。例如：

```python
from onebot import OneBot
from onebot.parameter import GetAPP

robot = OneBot(host='localhost', port=3001)

@robot.listener()
async def test(app1: OneBot, app2: OneBot = GetAPP()):
    print(app1, app2)
```

### 注入器列表
-   [GetAPP](#GetAPP)


#### GetAPP