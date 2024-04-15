from collections import deque

from onebot.exceptions import BuildMessageError


class MessageBuilder:
    def __init__(self):
        self._message = deque()
        self._cqs = deque()
        self._exists = set()

    def __iter__(self):
        return iter(self._message)

    def __str__(self):
        return ''.join(self._cqs)

    def __list(self):
        return self._message

    def video(self, file: str):
        if len(self._message) > 0:
            raise BuildMessageError('视频为独立消息，不能和其他消息一同发送')
        self._message.append({
            'type': 'video',
            'data': {
                'file': file
            }
        })
        self._cqs.append(f'[type=video,file={file}]')
        return self

    def record(self, file: str):
        if len(self._message) > 0:
            raise BuildMessageError('语音是独立消息，不能和其他消息一同发送')
        self._message.append({
            'type': 'record',
            'data': {
                'file': file
            }
        })
        self._cqs.append(f'[type=record,file={file}]')
        return self

    def json(self, data: str):
        if len(self._message) > 0:
            raise BuildMessageError('JSON是独立消息，不能和其他消息一同发送')
        self._message.append({
            'type': 'json',
            'data': {
                'file': data
            }
        })
        self._cqs.append(f'[type=json,file={data}]')
        return self

    def file(self, file: str):
        if len(self._message) > 0:
            raise BuildMessageError('文件是独立消息，不能和其他消息一同发送')
        self._message.append({
            'type': 'file',
            'data': {
                'file': file
            }
        })
        self._cqs.append(f'[type=file,file={file}]')
        return self

    def text(self, text):
        self._message.append({
            'type': 'text',
            'data': {
                'text': text
            }
        })
        self._cqs.append(text)
        return self

    def image(self, file: str):
        self._message.append({
            'type': 'image',
            'data': {
                'file': file
            }
        })
        self._cqs.append(f'[type=image,file={file}]')
        return self

    def face(self, face_id: int):
        self._message.append({
            'type': 'face',
            'data': {
                'id': str(face_id)
            }
        })
        self._cqs.append(f'[type=face,id={face_id}]')
        return self

    def reply(self, message_id: int):
        if 'reply' in self._exists:
            raise BuildMessageError('仅可以设置一条消息回复')
        self._message.appendleft({
            'type': 'reply',
            'data': {
                'id': message_id
            }
        })
        self._cqs.appendleft(f'[type=reply,id={message_id}]')
        self._exists.add('reply')
        return self

    def at(self, qq: int):
        self._message.append({
            'type': 'at',
            'data': {
                'qq': qq
            }
        })
        self._cqs.append(f'[type=at,qq={qq}]')
        return self
