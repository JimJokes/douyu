import time
import socket

from packet import Packet
from utils import UnmatchedLengthError, ReplyMessage

import logging
logger = logging.getLogger('main.'+__name__)

HOST = 'openbarrage.douyutv.com'
PORT = 8601
IP = (HOST, PORT)


class Client:
    def __init__(self):
        self.s = None
        self.num = 0

    def connect(self):
        while True:
            try:
                self.s = socket.create_connection(IP)
                self.num = 0
                return self._success_reply()
            except (ConnectionResetError, ConnectionRefusedError) as e:
                logger.warning(e)
            except ConnectionAbortedError as e:
                logger.exception(e)

            self.num += 1
            if self.num > 30:
                self.num = 0
                return self._warn_reply()
            time.sleep(1)
            continue

    def send_msg(self, data):
        try:
            self.s.sendall(data)
            return self._success_reply()
        except Exception as e:
            logger.exception(e)

    def receive(self):
        try:
            header = self._receive_n_bytes(12)
            if len(header) == 12:
                data_len = Packet.header_sniff(header)
                data = self._receive_n_bytes(data_len)
                return self._success_reply(data=data)
        except ConnectionAbortedError as e:
            logger.exception(e)
            return self._error_reply()
        except (ConnectionRefusedError, ConnectionResetError):
            return self._error_reply()
        except UnmatchedLengthError:
            return self._error_reply(code=401)

    def disconnect(self):
        self.s.close()
        return self._success_reply()

    def _receive_n_bytes(self, n):
        data = b''
        while len(data) < n:
            chunk = self.s.recv(n-len(data))
            if chunk == b'':
                break
            data += chunk
        return data

    def _error_reply(self, code=400, err_str=None):
        return ReplyMessage(ReplyMessage.ERROR, code, err_str)

    def _warn_reply(self, code=300, warn_data=None):
        return ReplyMessage(ReplyMessage.WARNING, code, warn_data)

    def _success_reply(self, code=200, data=None):
        return ReplyMessage(ReplyMessage.SUCCESS, code, data)
