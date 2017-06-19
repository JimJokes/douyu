import socket
import threading
import time

from packet import Packet
from message import Message
import logging
logger = logging.getLogger('main.'+__name__)

HOST = 'openbarrage.douyutv.com'
PORT = 8601
IP = (HOST, PORT)

# test = ('ofijsd', 123)

MAX_RECV_SIZE = 4096


class Client:

    s = None
    buff = None
    msg_buff = None

    send_lock = threading.Lock()

    def __init__(self):
        self.s = None
        self.num = 0

    def connect(self):
        while True:
            try:
                self.disconnect()
                self.s = socket.create_connection(IP)
                self.num = 0
                return
            except (ConnectionAbortedError, ConnectionRefusedError, ConnectionResetError) as e:
                self.num += 1
                if self.num > 30:
                    yield Message({'type': 'error', 'code': '2000'})
                    self.num = 0
                time.sleep(1)
                continue
            except Exception as e:
                logger.exception(e)
                self.num += 1
                if self.num > 30:
                    yield Message({'type': 'error', 'code': '2000'})
                    self.num = 0
                time.sleep(1)
                continue

    def receive(self):

        self.buff = b''
        self.msg_buff = ''

        while True:

            try:
                data = self.s.recv(MAX_RECV_SIZE)
            except (ConnectionAbortedError, ConnectionResetError, ConnectionRefusedError) as e:
                for msg in self.connect():
                    yield msg
                continue
            except Exception as e:
                logger.exception(e)
                time.sleep(1)
                continue

            if not data:
                continue

            self.buff += data

            while True:

                packet = Packet.sniff(self.buff)
                if packet is None:
                    break

                self.buff = self.buff[packet.size():]

                try:
                    self.msg_buff += packet.body.decode('UTF-8')
                except UnicodeDecodeError as e:
                    logger.info(e)
                    pass

                while True:

                    message = Message.sniff(self.msg_buff)
                    if message is None:
                        break

                    self.msg_buff = self.msg_buff[(message.size() + 1):]

                    yield message

    def send_msg(self, message_body):
        self.send_lock.acquire()
        try:
            self.s.send_msg(Packet(Message(message_body).to_text()).to_raw())
        finally:
            self.send_lock.release()

    def disconnect(self):
        if self.s:
            self.s.close()
