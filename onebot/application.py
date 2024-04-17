import asyncio
import json
import sys
import uuid
from asyncio import Future
from typing import Dict, List, Optional, Union

import websockets
from loguru import logger
from websockets.exceptions import ConnectionClosed, ConnectionClosedOK, ConnectionClosedError

from onebot.dispatcher import dispatcher
from onebot.exceptionals import AuthenticationError, SendMessageError
from onebot.filter.interfaces import Filter
from onebot.routing import Router
from onebot.types import MessageBuilder, Login, Message, Friend, Group, GroupUser, Version


class OneBot:
    def __init__(self, host: str, port: int, token: str = None):
        self.loop = asyncio.get_event_loop()
        # Websocket
        self.ws = None
        self.uri = f'ws://{host}:{port}'
        self.headers = [('Authorization', f'Bearer {token}')] if token else []
        self.connection_state = False
        # 异步消息
        self.echo_response: Dict[str, asyncio.Future] = {}
        # 路由处理器
        self.router = Router()

    def listener(self, filters: List[Filter] = None):
        def decorator(func):
            self.router.register(func, filters)

        return decorator

    def on_event(self, event_type: str):
        return self.router.on_event(event_type)

    def crontab(self, spec: str):
        def decorator(func):
            self.router.crontab(func, spec, {'app': self, 'context': {}})
            return func
        return decorator

    async def _connect(self):
        self.connection = False
        while True:
            try:
                self.ws = await websockets.connect(uri=self.uri, extra_headers=self.headers)
                break
            except (ConnectionClosedError, ConnectionClosed, ConnectionClosedOK, ConnectionRefusedError):
                logger.error('连接失败, 等待10s重试...')
                await asyncio.sleep(10)
        recv_data = await self.ws.recv()
        json_data = json.loads(recv_data)
        if json_data.get('retcode') == 1403:
            raise AuthenticationError()
        logger.info('websocket连接成功！')
        self.connection = True

    async def _close(self):
        if self.connection:
            await self.ws.close()

    async def _recv(self):
        while True:
            try:
                recv_data = await self.ws.recv()
                logger.debug(recv_data)
                scope = {
                    'request': json.loads(recv_data),
                    'app': self,
                    'router': self.router,
                    'context': {}
                }
                self.loop.create_task(dispatcher.handler(scope))
            except (ConnectionClosedError, ConnectionClosedOK):
                await self._connect()

    def run(self, log_level='INFO'):
        """
        启动入口
        :param log_level:   日志等级
        """
        # 删除默认日志,并设置日志
        logger.remove()
        logger.add(sys.stdout, level=log_level)
        try:
            self.loop.run_until_complete(self._connect())
            self.loop.create_task(self._recv())
            self.loop.create_task(self.router.startup({'app': self}))
            self.loop.run_forever()
        except KeyboardInterrupt:
            self.loop.run_until_complete(self.router.shutdown({'app': self}))
            self.loop.run_until_complete(self._close())

    def set_response(self, echo: str, response: dict):
        """
        异步消息回调
        :param echo: echo标识
        :param response: 消息内容
        :return:
        """
        if echo in self.echo_response:
            self.echo_response[echo].set_result(response)

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
            logger.info('发送消息 - 群组: {} 消息内容：{}', group_id, message)
        elif isinstance(message, MessageBuilder):
            message_chain = list(message)
            logger.info('发送消息 - 群组: {} 消息内容：{}', group_id, str(message))
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
            self,
            user_id: int,
            message: Union[str, MessageBuilder]
    ) -> int:
        if isinstance(message, str):
            message_chain = [{'type': 'text', 'data': {'text': message}}]
            logger.info('发送消息 - 用户: {}  消息内容：{}', user_id, message)
        elif isinstance(message, MessageBuilder):
            message_chain = list(message)
            logger.info('发送消息 - 用户: {} 消息内容：{}', user_id, str(message))
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
        response = await self._send_message({
            'action': 'set_group_whole_ban',
            'params': {
                'group_id': group_id,
                'enable': enable
            }
        })
        return response.get('status') == 'ok'

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

    async def _send_message(self, message: dict):
        message_id = uuid.uuid4().hex
        message['echo'] = message_id
        future = Future()
        self.echo_response[message_id] = future
        await self.ws.send(json.dumps(message))
        try:
            return await asyncio.wait_for(future, 10)
        finally:
            del self.echo_response[message_id]
