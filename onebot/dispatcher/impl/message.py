from abc import abstractmethod, ABC
from typing import List, Type

from loguru import logger

from onebot.dispatcher.interfaces import EventDispatcher
from onebot.types import At, Text, Json, Image, Face, Record, File, Reply, Video


class Processor(ABC):
    @abstractmethod
    def process(self, data: dict, scope: dict) -> None:
        pass

    @property
    @abstractmethod
    def type(self) -> str:
        pass


class AtProcessor(Processor):
    type = 'at'

    def process(self, data: dict, scope: dict) -> None:
        if self.type not in scope:
            scope[self.type] = set()
        scope[self.type].add(data['qq'])
        scope['message_chain'].append(At.model_validate(data))


class TextProcessor(Processor):
    type = 'text'

    def process(self, data: dict, scope: dict) -> None:
        if self.type not in scope:
            scope[self.type] = list()
        scope[self.type].append(data['text'])
        scope['message_chain'].append(Text.model_validate(data))


class JsonProcessor(Processor):
    type = 'json'

    def process(self, data: dict, scope: dict) -> None:
        scope[self.type] = data['data']
        scope['message_chain'].append(Json.model_validate(data))


class ImageProcessor(Processor):
    type = 'image'

    def process(self, data: dict, scope: dict) -> None:
        if self.type not in scope:
            scope[self.type] = list()
        model = Image.model_validate(data)
        scope[self.type].append(model)
        scope['message_chain'].append(model)


class FaceProcessor(Processor):
    type = 'face'

    def process(self, data: dict, scope: dict) -> None:
        if self.type not in scope:
            scope[self.type] = list()
        scope[self.type].append(data['id'])
        scope['message_chain'].append(Face.model_validate(data))


class RecordProcessor(Processor):
    type = 'record'

    def process(self, data: dict, scope: dict) -> None:
        model = Record.model_validate(data)
        scope[self.type] = model
        scope['message_chain'].append(model)


class VideoProcessor(Processor):
    type = 'video'

    def process(self, data: dict, scope: dict) -> None:
        model = Video.model_validate(data)
        scope['video'] = model
        scope['message_chain'].append(model)


class FileProcessor(Processor):
    type = 'file'

    def process(self, data: dict, scope: dict) -> None:
        model = File.model_validate(data)
        scope['file'] = model
        scope['message_chain'].append(model)


class ReplyProcessor(Processor):
    type = 'reply'

    def process(self, data: dict, scope: dict) -> None:
        scope['reply'] = data['id']
        scope['message_chain'].append(Reply.model_validate(data))


class MessageProcessing:
    strategies = {}

    def __init__(self, processors: List[Type[Processor]] = None):
        if processors is not None:
            for processor in processors:
                self.strategies[processor.type] = processor()

    def process(self, messages: list, scope: dict):
        scope['message_chain'] = []
        for message in messages:
            message_type = message['type']
            if message_type not in self.strategies:
                continue
            strategy = self.strategies.get(message_type)
            strategy.process(message['data'], scope)

    def add_processor(self, processor: Type[Processor]):
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


class MessageEventHandler(EventDispatcher):
    async def support(self, scope: dict) -> bool:
        return scope['request'].get('post_type') == 'message'

    async def handle(self, scope: dict):
        request = scope['request']
        if 'group_id' in request:
            logger.info("收到消息 - 群号: {group_id} 用户: {user_id} 消息内容: {raw_message}", **request)
        else:
            logger.info("收到消息 - 用户: {user_id} 消息内容: {raw_message}", **request)
        router = scope['router']
        message_process_factory.process(scope['request']['message'], scope)
        await router(scope)
