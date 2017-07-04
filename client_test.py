import time
import socket
import threading

from packet import Packet
from utils import UnmatchedLengthError

import logging
logger = logging.getLogger('main.'+__name__)

HOST = 'openbarrage.douyutv.com'
PORT = 8601
IP = (HOST, PORT)


class ReplyMessage:
    def __init__(self, status, code, data=None):
        self.status = status
        self.code = code
        self.data = data


class Client:
    Lock = threading.Lock()

    def __init__(self):
        self.sock = None

    def connect(self):
        try:
            self.sock = socket.create_connection(IP)
            self.sock.settimeout(600)
            return self._success_reply()
        except (ConnectionResetError, ConnectionRefusedError) as e:
            logger.warning(e)
        except ConnectionAbortedError as e:
            logger.exception(e)
        return self._error_reply()

    def send_msg(self, data):
        self.Lock.acquire()
        try:
            self.sock.sendall(data)
            return self._success_reply()
        except Exception as e:
            logger.exception(e)
        finally:
            self.Lock.release()

    def receive(self):
        try:
            header = self._receive_n_bytes(12)
            if len(header) == 12:
                data_len = Packet.header_sniff(header)
                data = self._receive_n_bytes(data_len)
                return self._success_reply(data=data)
        except UnmatchedLengthError as e:
            logger.info(e)
        except ConnectionAbortedError as e:
            logger.exception(e)
        except (ConnectionRefusedError, ConnectionResetError, socket.timeout):
            pass
        return self._error_reply()

    def disconnect(self):
        self.sock.close()
        return self._success_reply()

    def _receive_n_bytes(self, n):
        data = b''
        while len(data) < n:
            chunk = self.sock.recv(n - len(data))
            if chunk == b'':
                break
            data += chunk
        return data

    def _error_reply(self, code=400):
        return ReplyMessage(False, code)

    def _success_reply(self, code=200, data=None):
        return ReplyMessage(True, code, data=data)
