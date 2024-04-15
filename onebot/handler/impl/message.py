import json
from abc import ABC, abstractmethod
from typing import Type

from loguru import logger

from onebot.dtypes.models import *
from onebot.events.interfaces import EventHandler


class MessageProcessor(ABC):
    type: str

    @abstractmethod
    def process(self, type_: str, data: dict, context: dict) -> None:
        pass


class AtProcessor(MessageProcessor):
    type = 'at'

    def process(self, type_: str, data: dict, context: dict) -> None:
        if type_ not in context:
            context[type_] = set()
        context[type_].add(data['qq'])
        context['message_chain'].append(At.model_validate(data))


class TextProcessor(MessageProcessor):
    type = 'text'

    def process(self, type_: str, data: dict, context: dict) -> None:
        if type_ not in context:
            context[type_] = list()
        context[type_].append(data['text'])
        context['message_chain'].append(Text.model_validate(data))


class JsonProcessor(MessageProcessor):
    type = 'json'

    def process(self, type_: str, data: dict, context: dict) -> None:
        context['json'] = data['data']
        context['message_chain'].append(Json.model_validate(data))


class ImageProcessor(MessageProcessor):
    type = 'image'

    def process(self, type_: str, data: dict, context: dict) -> None:
        if type_ not in context:
            context[type_] = list()
        model = Image.model_validate(data)
        context[type_].append(model)
        context['message_chain'].append(model)


class FaceProcessor(MessageProcessor):
    type = 'face'

    def process(self, type_: str, data: dict, context: dict) -> None:
        if type_ not in context:
            context[type_] = list()
        context[type_].append(data['id'])
        context['message_chain'].append(Face.model_validate(data))


class RecordProcessor(MessageProcessor):
    type = 'record'

    def process(self, type_: str, data: dict, context: dict) -> None:
        model = Record.model_validate(data)
        context[type_] = model
        context['message_chain'].append(model)


class VideoProcessor(MessageProcessor):
    type = 'video'

    def process(self, type_: str, data: dict, context: dict) -> None:
        model = Video.model_validate(data)
        context['video'] = model
        context['message_chain'].append(model)


class FileProcessor(MessageProcessor):
    type = 'file'

    def process(self, type_: str, data: dict, context: dict) -> None:
        model = File.model_validate(data)
        context['file'] = model
        context['message_chain'].append(model)


class ReplyProcessor(MessageProcessor):
    type = 'reply'

    def process(self, type_: str, data: dict, context: dict) -> None:
        context['reply'] = data['id']
        context['message_chain'].append(Reply.model_validate(data))


class MessageProcessing:
    strategies = {}

    def __init__(self, processors: List[Type[MessageProcessor]] = None):
        if processors is not None:
            for processor in processors:
                self.strategies[processor.type] = processor()

    def process(self, messages: list, context: dict) -> dict:
        context['message_chain'] = []
        for message in messages:
            message_type = message['type']
            if message_type not in self.strategies:
                continue
            message_data = message['data']
            strategy = self.strategies.get(message_type)
            strategy.process(message_type, message_data, context)
        return context

    def add_processor(self, processor: Type[MessageProcessor]):
        self.strategies[processor.type] = processor()


message_process_factory = MessageProcessing([
    TextProcessor,
    AtProcessor,
    JsonProcessor,
    ImageProcessor,
    FaceProcessor,
    FileProcessor,
    RecordProcessor,
    VideoProcessor,
    ReplyProcessor,
])


class MessageEventHandler(EventHandler):

    async def support(self, context: dict, g_context: dict) -> bool:
        return context['request'].get('post_type') == 'message'

    async def handler(self, context: dict, g_context: dict):
        message = context['request']
        if 'group_id' in message:
            logger.info(
                "收到消息 - 群号: {} 用户: {} 消息内容: {}",
                message['group_id'],
                message['user_id'],
                message['raw_message']
            )
        else:
            logger.info(
                "收到消息 - 用户: {} 消息内容: {}",
                message['user_id'],
                message['raw_message']
            )
        message_process_factory.process(message['message'], context)
        app = g_context.get('app')
        await app.handler_manager.message_handler(context, g_context)