from struct import pack, unpack
from logger import Logger
logger = Logger(__name__)

MESSAGE_TYPE_FROM_CLIENT = 689
MESSAGE_TYPE_FROM_SERVER = 690


class Packet:

    body = None

    def __init__(self, body):
        self.body = body

    def to_raw(self):
        raw_length = len(self.body) + 9
        msg_type = MESSAGE_TYPE_FROM_CLIENT
        return pack('<llhbb%ds' % (len(self.body) + 1), raw_length, raw_length,
                    msg_type, 0, 0, (self.body + '\0').encode())

    def size(self):
        if self.body is None:
            return 0
        return len(self.body) + 12

    @staticmethod
    def sniff(buff):

        buff_len = len(buff)

        if buff_len < 12:
            return None

        packet_length_1, packet_length_2, msg_type, encryption, reserved, body = unpack('<llhbb%ds' % (buff_len - 12), buff)

        if packet_length_1 != packet_length_2:
            # print(packet_length_1 + packet_length_2)
            # print(body)
            logger.warning('[Packet] Unmatched packet length fields!')
            return None

        needed_body_length = packet_length_1 - 8
        current_body_length = len(body)

        if current_body_length < needed_body_length:
            return None

        if current_body_length > needed_body_length:
            body = body[0:needed_body_length]

        return Packet(body)
