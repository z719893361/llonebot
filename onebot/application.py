from __future__ import annotations

import asyncio
import json
import sys
import uuid

import websockets

from asyncio import Future
from typing import List, Union, Any, Dict
from loguru import logger

from .dtypes import MessageBuilder
from .dtypes.models import Login, Friend, Group, Message
from .exceptions import SendMessageError
from .fliters import Filter
from .handlers import event_dispatcher, HandlerRegister


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
        self.extra_headers = []
        if token is not None:
            self.extra_headers.append(('Authorization', f'Bearer {token}'))
        # 机器人ID
        self.robot_id: str = ''
        # 消息处理器
        self.handlers = HandlerRegister()
        # 消息响应
        self.message_response: Dict[Any, Future] = {}
        # 事件循环
        self.loop = asyncio.get_event_loop()

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
            self.handlers.register(func, order, first_over, filters, nullable, skipnull)

        return decorator

    async def _receiver(self):
        """
        消息接收和处理
        """
        while True:
            try:
                self.websocket = await websockets.connect(self._url, extra_headers=self.extra_headers)
                logger.info('websocket连接成功！')
                while True:
                    data = await self.websocket.recv()
                    logger.debug(data)
                    self.loop.create_task(event_dispatcher.handler(self, json.loads(data), {}))
            except (websockets.exceptions.ConnectionClosedError, ConnectionRefusedError):
                logger.error('连接异常，等待 10 秒后重试')
                await asyncio.sleep(10)

    def run(self, log_level='INFO'):
        # 设置日志
        logger.remove()
        logger.add(sys.stdout, level=log_level)
        try:
            self.loop.run_until_complete(self._receiver())
        except KeyboardInterrupt:
            logger.info('shutdown')

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
        await self.websocket.send(json.dumps(message))
        try:
            return await asyncio.wait_for(future, 10)
        finally:
            del self.message_response[message_id]

    def set_response(self, message_id: Any, message: Any):
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
            'action': 'send_group_msg',
            'params': {
                'user_id': user_id,
                'message': message_chain
            }
        })
        if response.get('status') == 'ok':
            return response['data']['message_id']
        else:
            raise SendMessageError(json.dumps(response))

    async def get_msg(self, message_id: int) -> Message:
        """
        获取消息
        :param message_id:  消息ID
        :return:   MsgInfo实体类
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
        await self._send_message({
            'action': 'delete_msg',
            'params': {
                'message_id': message_id
            }
        })

    async def send_like(self, user_id: int, times: int) -> None:
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
        print(response)

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
            'action': 'get_group_list',
            'params': {

            }
        })
        if response.get('status') == 'ok':
            return [Group.model_validate(group_info) for group_info in response.get('data', [])]

    async def get_group_info(self, group_id: int, no_cache: bool) -> Group:
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

    async def get_group_member_list(self, group_id: int):
        """
        获取群成员列表
        :param group_id:
        :return:
        """
        await self._send_message({
            'action': 'get_group_member_list',
            'params': {
                'group_id': group_id,
            }
        })

    async def get_group_member_info(self, group_id: int, user_id: int, no_cache: bool = False):
        """
        获取群成员信息

        :param group_id:    群号
        :param user_id:     QQ号
        :param no_cache:    是否使用缓存
        :return:
        """
        await self._send_message({
            'action': 'get_group_member_list',
            'params': {
                'group_id': group_id,
                'user_id': user_id,
                'no_cache': no_cache
            }
        })

    async def set_group_add_request(self, flag: str, sub_type: str, approve: bool, reason: str = ''):
        """
        加群请求
        :param flag:        加群请求的 flag（需从上报的数据中获得）
        :param sub_type:    add 或 invite，请求类型（需要和上报消息中的 sub_type 字段相符）
        :param approve:     是否同意请求／邀请
        :param reason:      拒绝理由（仅在拒绝时有效）
        :return:
        """
        await self._send_message({
            'action': 'set_group_add_request',
            'params': {
                'flag': flag,
                'sub_type': sub_type,
                'approve': approve,
                'reason': reason,
            }
        })

    async def set_group_leave(self, group_id: int, is_dismiss: bool):
        """
        退群
        :param group_id:    群号
        :param is_dismiss:  是否解散，如果登录号是群主，则仅在此项为 true 时能够解散
        :return:
        """
        await self._send_message({
            'action': 'set_group_leave',
            'params': {
                'group_id': group_id,
                'is_dismiss': is_dismiss,
            }
        })

    async def set_group_kick(self, group_id: int, user_id: int, reject_add_request: bool):
        """
        群组踢人
        :param group_id:            群号
        :param user_id:             要踢的 QQ 号
        :param reject_add_request:  拒绝此人的加群请求
        :return:
        """
        await self._send_message({
            'action': 'set_group_kick',
            'params': {
                'group_id': group_id,
                'user_id': user_id,
                'reject_add_request': reject_add_request,
            }
        })

    async def set_group_ban(self, group_id: int, user_id: int, duration: int):
        """
        群组单人禁言
        :param group_id:    group_id
        :param user_id:     user_id
        :param duration:    duration
        :return:
        """
        await self._send_message({
            'action': 'set_group_ban',
            'params': {
                'group_id': group_id,
                'user_id': user_id,
                'duration': duration,
            }
        })

    async def set_group_whole_ban(self, group_id: int, enable: bool):
        """
        群组禁言
        :param group_id:    群主
        :param enable:
        :return:
        """
        await self._send_message({
            'action': 'set_group_whole_ban',
            'params': {
                'group_id': group_id,
                'enable': enable
            }
        })

    async def set_group_admin(self, group_id: int, user_id: int, enable: bool):
        """
        群组设置管理员
        :param group_id:    群号
        :param user_id:     要设置管理员的 QQ 号
        :param enable:      true 为设置，false 为取消
        :return:
        """
        await self._send_message({
            'action': 'set_group_admin',
            'params': {
                'group_id': group_id,
                'user_id': user_id,
                'enable': enable
            }
        })

    async def set_group_card(self, group_id: int, user_id: int, card: str):
        """
        设置群名片（群备注）
        :param group_id:    群号
        :param user_id:     要设置的 QQ 号
        :param card:        群名片内容，不填或空字符串表示删除群名片
        :return:
        """
        await self._send_message({
            'action': 'set_group_card',
            'params': {
                'group_id': group_id,
                'user_id': user_id,
                'card': card
            }
        })

    async def set_group_name(self, group_id: int, group_name: str):
        """
        设置群名
        :param group_id:
        :param group_name:
        :return:
        """
        await self._send_message({
            'action': 'set_group_name',
            'params': {
                'group_id': group_id,
                'group_name': group_name,
            }
        })

    async def get_stranger_info(self, user_id: int, no_cache: bool):
        """
        获取陌生人信息
        :param user_id:     QQ号
        :param no_cache:    是否不使用缓存（使用缓存可能更新不及时，但响应更快）
        :return:
        """
        await self._send_message({
            'action': 'set_group_name',
            'params': {
                'user_id': user_id,
                'no_cache': no_cache,
            }
        })

    async def get_version_info(self):
        """
        获取版本信息
        :return:
        """
        await self._send_message({
            'action': 'get_version_info',
        })

    async def get_status(self):
        """
        获取运行状态
        :return:
        """
        await self._send_message({
            'action': 'get_status',
        })

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

    async def get_image(self, file: str) -> str:
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
        return response['file']

    async def get_record(self, file: str, out_format: str) -> str:
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
        return response['file']

    async def get_file(self, file: str):
        response = await self._send_message({
            'action': 'get_record',
            'params': {
                'file': file,
                'out_format': file
            }
        })

    async def clean_cache(self):
        """
        清理QQ缓存
        :return:
        """
        await self._send_message({
            'action': 'clean_cache',
        })
