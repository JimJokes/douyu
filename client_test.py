import time
import socket
import threading

from packet import Packet
from utils import UnmatchedLengthError, ReplyMessage

import logging
logger = logging.getLogger('main.'+__name__)

HOST = 'openbarrage.douyutv.com'
PORT = 8601
IP = (HOST, PORT)


class Client:
    Lock = threading.Lock()

    def __init__(self):
        self.sock = None
        self.num = 0

    def connect(self):
        while True:
            try:
                self.sock = socket.create_connection(IP)
                self.sock.settimeout(600)
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
        except socket.timeout:
            return self._error_reply(code=402)
        except ConnectionAbortedError as e:
            logger.exception(e)
            return self._error_reply()
        except (ConnectionRefusedError, ConnectionResetError):
            return self._error_reply()
        except UnmatchedLengthError:
            return self._error_reply(code=401)

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

    def _error_reply(self, code=400, err_str=None):
        return ReplyMessage(ReplyMessage.ERROR, code, err_str)

    def _warn_reply(self, code=300, warn_data=None):
        return ReplyMessage(ReplyMessage.WARNING, code, warn_data)

    def _success_reply(self, code=200, data=None):
        return ReplyMessage(ReplyMessage.SUCCESS, code, data)
