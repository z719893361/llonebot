class MessageBuilder:
    def __init__(self):
        self.message = []

    def video(self, file: str):
        self.message = [{
            'type': 'video',
            'data': {
                'file': file
            }
        }]

        return self

    def record(self, file: str):
        self.message = [{
            'type': 'record',
            'data': {
                'file': file
            }
        }]
        return self

    def json(self, data: str):
        self.message = [{
            'type': 'json',
            'data': {
                'file': data
            }
        }]
        return self

    def file(self, file: str):
        self.message = [{
            'type': 'file',
            'data': {
                'file': file
            }
        }]
        return self

    def text(self, text):
        self.message.append({
            'type': 'text',
            'data': {
                'text': text
            }
        })
        return self

    def image(self, file: str):
        self.message.append({
            'type': 'image',
            'data': {
                'file': file
            }
        })
        return self

    def face(self, face_id: int):
        self.message.append({
            'type': 'face',
            'data': {
                'id': str(face_id)
            }
        })
        return self

    def reply(self, message_id: int):
        self.message.append({
            'type': 'reply',
            'data': {
                'id': message_id
            }
        })
        return self

    def at(self, qq: int):
        self.message.append({
            'type': 'at',
            'data': {
                'qq': qq
            }
        })
        return self
