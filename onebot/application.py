from __future__ import annotations

import asyncio
import json
import sys
import uuid

import websockets

from asyncio import Future
from typing import List, Union, Any, Dict, Optional
from loguru import logger

from websockets import ConnectionClosedError, ConnectionClosedOK

from .dtypes import MessageBuilder
from .dtypes.models import Login, Friend, Group, Message, GroupUser, Version
from .exceptions import SendMessageError, AuthenticationError
from .fliters import Filter
from .handlers import event_dispatcher, HandlerManager


class OneBot:

    def __init__(self, host: str, port: int, token: str = None):
        """
        :param host:   主机地址
        :param port:   接收端口
        """
        self._url = 'ws://{host}:{port}'.format(host=host, port=port)
        # websocket
        self._websocket = None
        # websocket headers
        self._headers = []
        if token is not None:
            self._headers.append(('Authorization', f'Bearer {token}'))
        # Websocket连接状态
        self.connect_state = False
        # 机器人ID
        self.robot_id: int = ...
        # 消息处理器
        self.task_manager = HandlerManager()
        # 消息响应
        self.message_response: Dict[Any, Future] = {}
        # 事件循环
        self.loop = asyncio.get_event_loop()
        # 定时任务上下文
        self._cron_context = {}

    def listener(
            self,
            order: int = 0,
            first_over: bool = False,
            filters: List[Filter] = None,
            nullable: bool = True,
            skipnull: bool = True
    ):
        """
        注册过滤器
        :param order:       优先级
        :param first_over:  首次匹配则结束, True: 触发第一次后就跳过
        :param filters:     过滤器
        :param nullable:    参数解析遇到None(解析失败, 没有返回结果)是否抛出错误
        :param skipnull:    如果参数解析结果为空值(解析失败，没有返回结果), True跳过函数调用, False继续调用(失败参数会传入None)
        :return:
        """
        if filters is None:
            filters = []

        def decorator(func):
            self.task_manager.register_handler(func, order, first_over, filters, nullable, skipnull)

        return decorator

    def crontab(self, cron: str):
        """
        定时任务
        :param cron:    执行时间
        :return:
        """

        def decorator(fn):
            self.task_manager.register_crontab(cron, fn, self)

        return decorator

    def startup(self):
        def decorator(fn):
            self.task_manager.register_event(fn, 'startup')

        return decorator

    def shutdown(self):
        def decorator(fn):
            self.task_manager.register_event(fn, 'shutdown')

        return decorator

    async def _connecting(self):
        self.connect_state = False
        while True:
            try:
                self._websocket = await websockets.connect(self._url, extra_headers=self._headers)
                break
            except (ConnectionRefusedError, websockets.exceptions.ConnectionClosedError):
                logger.error('连接失败，等待10秒重试...')
                await asyncio.sleep(10)
        message = await self._websocket.recv()
        message = json.loads(message)
        if message.get('retcode') == 1403:
            raise AuthenticationError('Token认证失败')
        logger.info('websocket连接成功！')
        self.connect_state = True

    async def _receiver(self):
        """
        消息接收并处理
        """
        while True:
            try:
                data = await self._websocket.recv()
                logger.debug(data)
                self.loop.create_task(event_dispatcher.handler(self, json.loads(data), {}))
            except (ConnectionClosedError, ConnectionClosedOK):
                await self._connecting()

    def run(self, log_level='INFO'):
        """
        启动入口
        :param log_level:   日志等级
        """
        # 删除默认日志
        logger.remove()
        # 添加日志
        logger.add(sys.stdout, level=log_level)
        # 连接WebSocket
        self.loop.run_until_complete(self._connecting())
        # 启动消息监听任务
        self.loop.create_task(self._receiver())
        # 调用启动事件
        self.loop.create_task(self.task_manager.execute_event_task('startup', self))
        try:
            self.loop.run_forever()
        except KeyboardInterrupt:
            # 调用结束事件
            self.loop.run_until_complete(self.task_manager.execute_event_task('shutdown', self))
            # 关闭websocket连接
            self.loop.run_until_complete(self._websocket.close())

    async def _send_message(self, message: dict) -> dict:
        """
        发送消息
        :param message: 消息
        :return:        消息ID
        """
        message_id = uuid.uuid4().hex
        future = Future()
        message['echo'] = message_id
        self.message_response[message_id] = future
        await self._websocket.send(json.dumps(message))
        try:
            return await asyncio.wait_for(future, 10)
        finally:
            del self.message_response[message_id]

    def set_response(self, message_id: Any, message: Any) -> None:
        """
        异步设置响应
        :param message_id:  消息ID
        :param message:     响应内容
        """
        if message_id in self.message_response:
            self.message_response[message_id].set_result(message)

    async def get_login_info(self) -> Login:
        """
        获取登录信息
        :return:
        """
        response = await self._send_message({
            'action': 'get_login_info'
        })
        if response.get('status') == 'ok':
            return Login.model_validate(response['data'])

    async def send_group_msg(
            self,
            group_id: int,
            message: Union[str, MessageBuilder],
    ) -> int:
        """
        :param group_id:    群号
        :param message:     消息
        :return:
        """
        if isinstance(message, str):
            message_chain = [{'type': 'text', 'data': {'text': message}}]
        elif isinstance(message, MessageBuilder):
            message_chain = message.to_list()
        else:
            raise SendMessageError('message参数类型错误')
        response = await self._send_message({
            'action': 'send_group_msg',
            'params': {
                'group_id': group_id,
                'message': message_chain
            }
        })
        if response.get('status') == 'ok':
            return response['data']['message_id']
        else:
            raise SendMessageError(json.dumps(response))

    async def send_private_msg(
            self, user_id: int,
            message: Union[str, MessageBuilder]
    ) -> int:
        if isinstance(message, str):
            message_chain = [{'type': 'text', 'data': {'text': message}}]
        elif isinstance(message, MessageBuilder):
            message_chain = message.to_list()
        else:
            raise SendMessageError('参数类型错误')
        response = await self._send_message({
            'action': 'send_private_msg',
            'params': {
                'user_id': user_id,
                'message': message_chain
            }
        })
        if response.get('status') == 'ok':
            return response['data']['message_id']
        else:
            raise SendMessageError(json.dumps(response))

    async def get_msg(self, message_id: int) -> Optional[Message]:
        """
        获取消息
        :param message_id:  消息ID
        :return: MsgInfo实体类
        """
        response = await self._send_message({
            'action': 'get_msg',
            'params': {
                'message_id': message_id
            }
        })
        if response.get('status') == 'ok':
            return Message.model_validate(response['data'])

    async def delete_msg(self, message_id: int) -> None:
        """
        撤回消息
        :param message_id:
        :return:
        """
        response = await self._send_message({
            'action': 'delete_msg',
            'params': {
                'message_id': message_id
            }
        })
        return response.get('status') == 'ok'

    async def send_like(self, user_id: int, times: int) -> bool:
        """
        好友点赞
        :param user_id: QQ
        :param times:   次数
        :return:
        """
        response = await self._send_message({
            'action': 'send_like',
            'params': {
                'user_id': user_id,
                'times': times
            }
        })
        return response.get('status') == 'ok'

    async def get_friend_info(self, user_id: int, no_cache: bool = False) -> Optional[Friend]:
        """
        获取好友信息(目前尚不能获取陌生人信息)
        :param user_id:     QQ号
        :param no_cache:    是否不使用缓存（使用缓存可能更新不及时，但响应更快）
        :return:
        """
        response = await self._send_message({
            'action': 'get_stranger_info',
            'params': {
                'user_id': user_id,
                'no_cache': no_cache,
            }
        })
        if response.get('status') == 'ok':
            return Friend.model_validate(response['data'])

    async def get_friend_list(self) -> List[Friend]:
        """
        获取好友列表
        :return:
        """
        response = await self._send_message({
            'action': 'get_friend_list'
        })
        if response.get('status') == 'ok':
            return [Friend.model_validate(friend) for friend in response['data']]

    async def set_friend_add_request(self, flag: str, approve: bool) -> bool:
        """
        处理加好友请求

        :param flag:    加好友请求的 flag（需从上报的数据中获得）
        :param approve: 是否同意请求
        :return:
        """
        response = await self._send_message({
            'action': 'set_friend_add_request',
            'params': {
                'flag': flag,
                'approve': approve,
            }
        })
        return response.get('status') == 'ok'

    async def get_group_list(self) -> List[Group]:
        """
        获取群列表
        :return:
        """
        response = await self._send_message({
            'action': 'get_group_list'
        })
        if response.get('status') == 'ok':
            return [Group.model_validate(group_info) for group_info in response.get('data', [])]

    async def get_group_info(self, group_id: int, no_cache: bool) -> Optional[Group]:
        """
        获取群信息
        :param group_id:  群号
        :param no_cache:  是否不使用缓存（使用缓存可能更新不及时，但响应更快）
        :return:
        """
        response = await self._send_message({
            'action': 'get_group_info',
            'params': {
                'group_id': group_id,
                'no_cache': no_cache
            }
        })
        if response.get('status') == 'ok':
            return Group.model_validate(response['data'])

    async def get_group_member_list(self, group_id: int) -> List[GroupUser]:
        """
        获取群成员列表
        :param group_id:
        :return:
        """
        response = await self._send_message({
            'action': 'get_group_member_list',
            'params': {
                'group_id': group_id,
            }
        })
        if response.get('status') == 'ok':
            return [GroupUser.model_validate(row) for row in response['data']]

    async def get_group_member_info(self, group_id: int, user_id: int, no_cache: bool = False) -> Optional[GroupUser]:
        """
        获取群成员信息

        :param group_id:    群号
        :param user_id:     QQ号
        :param no_cache:    是否使用缓存
        :return:
        """
        response = await self._send_message({
            'action': 'get_group_member_info',
            'params': {
                'group_id': group_id,
                'user_id': user_id,
                'no_cache': no_cache
            }
        })
        if response.get('status') == 'ok':
            return GroupUser.model_validate(response['data'])

    async def set_group_add_request(self, flag: str, sub_type: str, approve: bool, reason: str = '') -> bool:
        """
        加群请求
        :param flag:        加群请求的 flag（需从上报的数据中获得）
        :param sub_type:    add 或 invite，请求类型（需要和上报消息中的 sub_type 字段相符）
        :param approve:     是否同意请求／邀请
        :param reason:      拒绝理由（仅在拒绝时有效）
        :return:
        """
        response = await self._send_message({
            'action': 'set_group_add_request',
            'params': {
                'flag': flag,
                'sub_type': sub_type,
                'approve': approve,
                'reason': reason,
            }
        })
        return response.get('status') == 'ok'

    async def set_group_leave(self, group_id: int, is_dismiss: bool = False) -> bool:
        """
        退群
        :param group_id:    群号
        :param is_dismiss:  是否解散，如果登录号是群主，则仅在此项为 true 时能够解散
        :return:
        """
        response = await self._send_message({
            'action': 'set_group_leave',
            'params': {
                'group_id': group_id,
                'is_dismiss': is_dismiss,
            }
        })
        return response.get('status') == 'ok'

    async def set_group_kick(self, group_id: int, user_id: int, reject_add_request: bool = False) -> bool:
        """
        群组踢人
        :param group_id:            群号
        :param user_id:             要踢的 QQ 号
        :param reject_add_request:  拒绝此人的加群请求
        :return:
        """
        response = await self._send_message({
            'action': 'set_group_kick',
            'params': {
                'group_id': group_id,
                'user_id': user_id,
                'reject_add_request': reject_add_request,
            }
        })
        return response.get('status') == 'ok'

    async def set_group_ban(self, group_id: int, user_id: int, duration: int) -> bool:
        """
        群组单人禁言
        :param group_id:    group_id
        :param user_id:     user_id
        :param duration:    duration
        :return:
        """
        response = await self._send_message({
            'action': 'set_group_ban',
            'params': {
                'group_id': group_id,
                'user_id': user_id,
                'duration': duration,
            }
        })
        return response.get('status') == 'ok'

    async def set_group_whole_ban(self, group_id: int, enable: bool) -> bool:
        """
        群组禁言
        :param group_id:    群号
        :param enable:      开启 or 关闭
        :return:
        """
        await self._send_message({
            'action': 'set_group_whole_ban',
            'params': {
                'group_id': group_id,
                'enable': enable
            }
        })

    async def set_group_admin(self, group_id: int, user_id: int, enable: bool) -> bool:
        """
        群组设置管理员
        :param group_id:    群号
        :param user_id:     要设置管理员的 QQ 号
        :param enable:      True 为设置, False为取消
        :return:
        """
        response = await self._send_message({
            'action': 'set_group_admin',
            'params': {
                'group_id': group_id,
                'user_id': user_id,
                'enable': enable
            }
        })
        return response.get('status') == 'ok'

    async def set_group_card(self, group_id: int, user_id: int, card: str) -> bool:
        """
        设置群名片（群备注）
        :param group_id:    群号
        :param user_id:     要设置的 QQ 号
        :param card:        群名片内容，不填或空字符串表示删除群名片
        :return:
        """
        response = await self._send_message({
            'action': 'set_group_card',
            'params': {
                'group_id': group_id,
                'user_id': user_id,
                'card': card
            }
        })
        return response.get('status') == 'ok'

    async def set_group_name(self, group_id: int, group_name: str) -> bool:
        """
        设置群名
        :param group_id:
        :param group_name:
        :return:
        """
        response = await self._send_message({
            'action': 'set_group_name',
            'params': {
                'group_id': group_id,
                'group_name': group_name,
            }
        })
        return response.get('status') == 'ok'

    async def get_version_info(self) -> Optional[Version]:
        """
        获取版本信息
        :return:
        """
        response = await self._send_message({
            'action': 'get_version_info',
        })
        if response.get('status') == 'ok':
            return Version.model_validate(response['data'])

    async def get_status(self):
        """
        获取运行状态
        :return:
        """
        response = await self._send_message({
            'action': 'get_status',
        })
        return response.get('status') == 'ok'

    async def can_send_image(self) -> bool:
        """
        检查是否可以发送图片
        :return:
        """
        response = await self._send_message({
            'action': 'get_status',
        })
        return response['yes']

    async def can_send_record(self) -> bool:
        """
        检查是否可以发送语音
        :return:
        """
        response = await self._send_message({
            'action': 'can_send_record',
        })
        return response['yes']

    async def get_image(self, file: str) -> Optional[str]:
        """
        获取图片详情
        :param file:    收到的图片文件名（消息段的 file 参数），如 6B4DE3DFD1BD271E3297859D41C530F5.jpg
        :return:
        """
        response = await self._send_message({
            'action': 'get_image',
            'params': {
                'file': file,
            }
        })
        if response.get('status') == 'ok':
            return response['data']['file']

    async def get_record(self, file: str, out_format: str) -> Optional[str]:
        """
        获取语音文件
        :param file:        收到的语音文件名（消息段的 file 参数），如 0B38145AA44505000B38145AA4450500.silk
        :param out_format:  要转换到的格式，目前支持 mp3、amr、wma、m4a、spx、ogg、wav、flac
        :return:
        """
        response = await self._send_message({
            'action': 'get_record',
            'params': {
                'file': file,
                'out_format': out_format
            }
        })
        if response.get('status') == 'ok':
            return response['data']['file']

    async def get_file(self, file: str) -> Optional[str]:
        response = await self._send_message({
            'action': 'get_file',
            'params': {
                'file_id': file,
            }
        })
        if response.get('status') == 'ok':
            return response['data']['file']

    async def clean_cache(self) -> bool:
        """
        清理QQ缓存
        :return:
        """
        response = await self._send_message({
            'action': 'clean_cache',
        })
        return response.get('status') == 'ok'
