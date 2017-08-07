from utils import deserialize, serialize


class Message:

    body = None

    def __init__(self, body):
        self.body = body

    def __getattr__(self, item):
        if self.body is None:
            return None
        try:
            value = self.body[item]
            return value
        except KeyError:
            return None

    def to_text(self):
        return serialize(self.body)

    @staticmethod
    def sniff(buff):

        if buff is None or len(buff) <= 0:
            return None

        msg_bodies = buff.split('\0')
        if len(msg_bodies) <= 1:
            return None

        return Message.from_raw(msg_bodies[0])

    @staticmethod
    def from_raw(raw):
        result = Message(deserialize(raw))
        result._serialized_size = len(raw)
        return result
