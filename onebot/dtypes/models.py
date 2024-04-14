from __future__ import annotations

from typing import List, Optional, Literal

from onebot.dtypes.enum import Gender, GroupRole

from pydantic import BaseModel, Field


class Text(BaseModel):
    """
    文本
    """
    # 文本内容
    text: str


class Face(BaseModel):
    """
    表情
    """
    # 表情ID
    id: str


class Image(BaseModel):
    """
    图片
    """
    # 图片文件名
    file: str
    # 图片 URL
    url: Optional[str] = None
    # 缓存
    cache: Optional[Literal[0, 1]] = 1
    # 只在通过网络 URL 发送时有效，表示是否通过代理下载文件 需通过环境变量或配置文件配置代理
    proxy: Optional[Literal[0, 1]] = 1
    # 超时
    timeout: Optional[float] = None
    # 图片大小
    file_size: int = None


class Record(BaseModel):
    """
    语音
    """
    # 语音文件名
    file: str
    # 语音存放路径
    path: Optional[str] = None
    # 文件大小
    file_size: Optional[int] = 0


class Video(BaseModel):
    """
    视频
    """
    # 视频文件名
    file: str
    # 视频路径
    path: str
    # 文件ID
    file_id: str
    # 文件大小
    file_size: int


class File(BaseModel):
    """
    文件
    """
    # 文件名
    file: str
    # 文件路径
    path: str
    # 文件ID
    file_id: str
    # 文件大小
    file_size: int


class At(BaseModel):
    """
    At
    """
    qq: str


class Json(BaseModel):
    """
    Json
    """
    data: str


class Reply(BaseModel):
    """
    消息回复
    """
    id: int


class FriendAddRequest(BaseModel):
    """
    好友请求
    """
    # 时间戳
    time: int
    # 发送请求的QQ号
    user_id: int
    # 验证信息
    comment: str
    # 请求flag，在调用处理请求的API时需要传入
    flag: str


class GroupAddRequest(BaseModel):
    """
    好友请求
    """
    # 时间戳
    time: int
    # 群号
    group_id: int
    # 发送请求的QQ号
    user_id: int
    # 验证信息
    comment: str
    # 请求flag，在调用处理请求的API时需要传入
    flag: str


class GroupInviteRequest(BaseModel):
    """
    好友请求
    """
    # 时间戳
    time: int
    # 群号
    group_id: int
    # 发送请求的QQ号
    user_id: int
    # 请求flag，在调用处理请求的API时需要传入
    flag: str
    # 事件类型
    sub_type: str


class Login(BaseModel):
    """
    登录信息
    """
    # 账号
    user_id: int
    # 昵称
    nickname: str


class Group(BaseModel):
    """
    群信息
    """
    # 群号
    group_id: int
    # 群昵称
    group_name: str
    # 人数
    member_count: int
    # 最大人数
    max_member_count: int


class Message(BaseModel):
    # 发送时间
    time: int
    # 消息类型，同 消息事件
    message_type: str
    # 消息ID
    message_id: int
    # 消息真实ID
    real_id: int
    # 发送人信息，同消息事件
    sender: Sender
    # 消息内容
    message: List


class Friend(BaseModel):
    # QQ号
    user_id: int
    # 昵称
    nickname: str
    # 备注
    remark: str
    # 性别
    sex: Gender
    # 等级
    level: int


class GroupUser(BaseModel):
    # 群号
    group_id: int
    # QQ 号
    user_id: int
    # 昵称
    nickname: str
    # 群名片／备注
    card: str
    # 性别
    sex: str
    # 年龄
    age: int
    # 地区
    area: str
    # 成员等级
    level: int
    # QQ等级
    qq_level: int
    # 加群时间戳
    join_time: int
    # 最后发言时间
    last_sent_time: int
    # 专属头衔过期时间戳
    title_expire_time: int
    # 是否不良记录成员
    unfriendly: bool
    # 是否允许修改群名片
    card_changeable: bool
    # 是否为机器人
    is_robot: bool
    # 禁言时间
    shut_up_timestamp: int
    # 身份
    role: str
    # 专属头衔
    title: str


class Sender(BaseModel):
    """
    消息发送人
    """
    # 用户QQ
    user_id: int
    # 用户昵称
    nickname: str
    # 用户角色
    role: GroupRole = Field(None)


class Version(BaseModel):
    """
    版本信息
    """
    app_name: str
    protocol_version: str
    app_version: str
