class SendMessageError(Exception):
    """
    发送消息错误
    """
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg
