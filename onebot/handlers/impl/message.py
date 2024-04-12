import json
from abc import ABC, abstractmethod
from typing import Type

from loguru import logger

from onebot.dtypes.models import *
from onebot.handlers.interfaces import EventHandler


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
        context['message'].append(At.model_validate(data))


class TextProcessor(MessageProcessor):
    type = 'text'

    def process(self, type_: str, data: dict, context: dict) -> None:
        if type_ not in context:
            context[type_] = list()
        context[type_].append(data['text'])
        context['message'].append(Text.model_validate(data))


class JsonProcessor(MessageProcessor):
    type = 'json'

    def process(self, type_: str, data: dict, context: dict) -> None:
        context['json'] = json.loads(data['data'])
        context['message'].append(Json.model_validate(data))


class ImageProcessor(MessageProcessor):
    type = 'image'

    def process(self, type_: str, data: dict, context: dict) -> None:
        if type_ not in context:
            context[type_] = list()
        model = Image.model_validate(data)
        context[type_].append(model)
        context['message'].append(model)


class FaceProcessor(MessageProcessor):
    type = 'face'

    def process(self, type_: str, data: dict, context: dict) -> None:
        if type_ not in context:
            context[type_] = list()
        context[type_].append(data['id'])
        context['message'].append(Face.model_validate(data))


class RecordProcessor(MessageProcessor):
    type = 'record'

    def process(self, type_: str, data: dict, context: dict) -> None:
        model = Record.model_validate(data)
        context[type_] = model
        context['message'].append(model)


class VideoProcessor(MessageProcessor):
    type = 'video'

    def process(self, type_: str, data: dict, context: dict) -> None:
        model = Video.model_validate(data)
        context['video'] = model
        context['message'].append(model)


class FileProcessor(MessageProcessor):
    type = 'file'

    def process(self, type_: str, data: dict, context: dict) -> None:
        model = File.model_validate(data)
        context['file'] = model
        context['message'].append(model)


class ReplyProcessor(MessageProcessor):
    type = 'reply'

    def process(self, type_: str, data: dict, context: dict) -> None:
        context['reply'] = data['id']
        context['message'].append(Reply.model_validate(data))


class MessageProcessing:
    strategies = {}

    def __init__(self, processors: List[Type[MessageProcessor]] = None):
        if processors is not None:
            for processor in processors:
                self.strategies[processor.type] = processor()

    def process(self, messages: list, context: dict) -> dict:
        context['message'] = []
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

    async def support(self, app, message: dict, context: dict) -> bool:
        return message.get('post_type') == 'message'

    async def handler(self, app, message: dict, context: dict):
        if 'group_id' in message:
            logger.info("群号: {} 用户: {} 消息内容: {}", message['group_id'], message['user_id'], message['raw_message'])
        else:
            logger.info("用户: {} 消息内容: {}", message['user_id'], message['raw_message'])
        context = {}
        message_process_factory.process(message['message'], context)
        await app.handlers.handler(app, message, context)
