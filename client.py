import logging
import os
import socket
import threading

logging.basicConfig(filename='information.log', level=logging.DEBUG,
                    format='%(asctime)s %(filename)s[line:%(lineno)s] %(levelname)s %(message)s',
                    datefmt='%y-%m-%d %H:%M:%S')

import time

from packet import Packet
from message import Message

HOST = 'openbarrage.douyutv.com'
PORT = 8601
IP = (HOST, PORT)

# test = ('ofijsd', 123)

MAX_RECV_SIZE = 4096

# msg_type = []
# type_file = os.path.join(os.path.dirname(__file__), 'msgtype')
# data_file = os.path.join(os.path.dirname(__file__), 'datas')

# if os.path.exists(type_file):
#     pass
# else:
#     with open(type_file, 'w') as q:
#         pass
#
# with open(type_file, 'r') as f:
#     lines = f.readlines()
#     for line in lines:
#         msg_type.append(line.strip())
#
#
# def write(msg, file):
#     if os.path.exists(file):
#         with open(file, 'a') as a:
#             try:
#                 a.write(msg + '\n')
#             except Exception as e:
#                 logging.warning(e)
#     else:
#         with open(file, 'w') as b:
#             try:
#                 b.write(msg + '\n')
#             except Exception as e:
#                 logging.warning(e)


class Client:

    s = None
    buff = None
    msg_buff = None

    send_lock = threading.Lock()

    def __init__(self):
        self.s = None

    def connect(self):
        while True:
            try:
                self.s = socket.create_connection(IP)
                return
            except Exception as e:
                logging.warning(e)
                time.sleep(1)
                continue

    def receive(self):

        self.buff = b''
        self.msg_buff = ''

        while True:

            try:
                data = self.s.recv(MAX_RECV_SIZE)
            except ConnectionAbortedError or ConnectionResetError as e1:
                logging.warning(e1)
                self.connect()
            except Exception as e:
                logging.exception(str(e))
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
                    # logging.info(e)
                    pass

                while True:

                    message = Message.sniff(self.msg_buff)
                    if message is None:
                        break

                    # msgtype = message.body['type']
                    # if msgtype not in msg_type:
                    #     msg_type.append(message.body['type'])
                    #     write(msgtype, type_file)
                    # msg_file = os.path.join(data_file, msgtype)
                    # write(self.msg_buff, msg_file)

                    self.msg_buff = self.msg_buff[(message.size() + 1):]

                    yield message

    def send(self, message_body):
        self.send_lock.acquire()
        try:
            self.s.send(Packet(Message(message_body).to_text()).to_raw())
        finally:
            self.send_lock.release()
