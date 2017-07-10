from struct import pack, unpack
from utils import UnmatchedLengthError
import logging
logger = logging.getLogger('main.'+__name__)

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

    @staticmethod
    def header_sniff(buff):
        packet_length_1, packet_length_2, msg_type, encryption, reserved = unpack('<llhbb', buff)

        if packet_length_1 != packet_length_2:
            raise UnmatchedLengthError('[Packet] Unmatched packet length fields!')

        return packet_length_1-8
