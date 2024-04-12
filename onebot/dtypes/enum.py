from enum import Enum


class PostType(Enum):
    """
    消息类型
    """
    # 事件
    meta_event = 'meta_event'
    # 消息
    message = 'message'
    # 通知
    notice = 'notice'


class MessageType(Enum):
    """
    消息类型枚举
    """
    # 群聊
    group = 'group'
    # 私聊
    private = 'private'
    # 通知
    notice = 'notice'


class GroupRole(Enum):
    """
    群组角色枚举
    """
    # 群主
    owner = 'owner'
    # 管理员
    admin = 'admin'
    # 群员
    member = 'member'


class Gender(Enum):
    """
    性别
    """
    # 未知
    unknown = 'unknown'
    # 男
    male = 'male'
    # 女
    female = 'female'
