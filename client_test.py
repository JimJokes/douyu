import os
import socket
import threading
import time

from packet import Packet
from message import Message
from utils import UnmatchedLengthError
import logging
logger = logging.getLogger('main.'+__name__)

HOST = 'openbarrage.douyutv.com'
PORT = 8601
IP = (HOST, PORT)

test = ('ofijsd', 123)

MAX_RECV_SIZE = 4096

# test
msg_type = []
type_file = os.path.join(os.path.dirname(__file__), 'msgtype')
data_file = os.path.join(os.path.dirname(__file__), 'datas')
if not os.path.exists(data_file):
    os.makedirs(data_file)

if os.path.exists(type_file):
    pass
else:
    with open(type_file, 'w') as q:
        pass

with open(type_file, 'r') as f:
    lines = f.readlines()
    for line in lines:
        msg_type.append(line.strip())


def write(msg, file):
    if os.path.exists(file):
        with open(file, 'a') as a:
            try:
                a.write(msg + '\n')
            except Exception as e:
                logger.warning(e)
    else:
        with open(file, 'w') as b:
            try:
                b.write(msg + '\n')
            except Exception as e:
                logger.warning(e)
# test


class ReplyMessage:
    ERROR, WARNING, SUCCESS = range(3)

    def __init__(self, msg_type, code, data=None):
        self.type = msg_type
        self.code = code
        self.data = data


class CommandMessage:
    CONNECT, SEND, RECEIVE, CLOSE = range(4)

    def __init__(self, msg_type, data=None):
        self.type = msg_type
        self.data = data


class Client:
    def __init__(self, result_q):
        self.result_q = result_q
        # self.s = None
        self.s = socket.create_connection(IP)
        self.num = 0

    def connect(self):
        while True:
            try:
                self.s = socket.create_connection(IP)
                self.result_q.put(self._success_reply(code=2001, data='连接弹幕服务器成功！'))
                self.num = 0
            except (ConnectionResetError, ConnectionRefusedError) as e:
                logger.warning(e)
            except ConnectionAbortedError as e:
                logger.exception(e)

            self.num += 1
            if self.num > 30:
                self.result_q.put(self._warn_reply(1999, '连接弹幕服务器失败，请重新连接！'))
                self.num = 0
            time.sleep(1)
            continue

    def send_msg(self, data):
        try:
            self.s.sendall(Packet(Message(data).to_text()).to_raw())
            self.result_q.put(self._success_reply(code=2002))
        except Exception as e:
            logger.exception(e)

    def receive(self):
        try:
            header = self._receive_n_bytes(12)
            if len(header) == 12:
                data_len = Packet.header_sniff(header)
                packet = Packet(self._receive_n_bytes(data_len))
                try:
                    msg_buff = packet.body.decode()
                    message = Message.sniff(msg_buff)
                    self.result_q.put(self._success_reply(message))
                except UnicodeDecodeError as e:
                    self.result_q.put(self._warn_reply(1998, e))
                    logger.info(packet.body)
        except ConnectionAbortedError as e:
            logger.exception(e)
            self.result_q.put(self._error_reply(9999, e))
        except (ConnectionRefusedError, ConnectionResetError) as e:
            self.result_q.put(self._error_reply(9999, e))
        except UnmatchedLengthError as e:
            self.result_q.put(self._error_reply(9998, e))

    def disconnect(self):
        self.s.close()
        self.result_q.put(self._success_reply(2003, '断开弹幕服务器连接成功！'))

    def _receive_n_bytes(self, n):
        data = b''
        while len(data) < n:
            chunk = self.s.recv(n-len(data))
            if chunk == b'':
                break
            data += chunk
        return data

    def _error_reply(self, code, err_str):
        return ReplyMessage(ReplyMessage.ERROR, code, err_str)

    def _warn_reply(self, code, warn_data):
        return ReplyMessage(ReplyMessage.WARNING, code, warn_data)

    def _success_reply(self, code=2000, data=None):
        return ReplyMessage(ReplyMessage.SUCCESS, code, data)
