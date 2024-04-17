import asyncio
import json
import sys
from typing import Dict, List

import websockets
from loguru import logger
from websockets.exceptions import ConnectionClosed, ConnectionClosedOK, ConnectionClosedError

from onebot.dispatcher import dispatcher
from onebot.exceptionals import AuthenticationError
from onebot.filter.interfaces import Filter
from onebot.router import Router


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
        #
        self.router = Router()

    def listener(self, filters: List[Filter] = None):
        def decorator(func):
            self.router.register(func, filters)
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
            self.loop.run_forever()
        except KeyboardInterrupt:
            self.loop.run_until_complete(self._close())

    async def set_response(self, echo_id: str, response: dict):
        if echo_id in response:
            self.echo_response[echo_id].set_result(response)
