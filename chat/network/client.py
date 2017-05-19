import socket
import threading
import os
from chat.network.packet import Packet
from chat.network.message import Message

HOST = 'openbarrage.douyutv.com'
PORT = 8601

MAX_RECV_SIZE = 4096

msg_type = []
msg_type_file = os.path.join(os.path.dirname(__file__), 'msgtype')

if os.path.exists(msg_type_file):
    pass
else:
    with open(msg_type_file, 'w') as q:
        pass

with open(msg_type_file, 'r') as f:
    lines = f.readlines()
    for line in lines:
        msg_type.append(line.strip())


def write(msg, name):
    data_file = os.path.join(os.path.dirname(__file__), 'datas')
    file = os.path.join(data_file, name)
    if os.path.exists(file):
        with open(file, 'a') as a:
            a.write(msg + '\n')
    else:
        with open(file, 'w') as b:
            b.write(msg + '\n')


class Client:

    s = None
    buff = None
    msg_buff = None

    send_lock = threading.Lock()

    def __init__(self):
        self.s = socket.create_connection((HOST, PORT))

    def receive(self):

        self.buff = b''
        self.msg_buff = ''

        while True:

            try:
                data = self.s.recv(MAX_RECV_SIZE)
            except Exception as e:
                print(e)
                continue

            if not data:
                # time.sleep(0.01)
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
                    print(e)
                    pass

                while True:

                    message = Message.sniff(self.msg_buff)
                    if message is None:
                        break

                    # print(self.msg_buff)
                    msgtype = message.body['type']
                    if msgtype not in msg_type:
                        msg_type.append(message.body['type'])
                    write(self.msg_buff, msgtype)
                    # print(msg_type)
                    # print(message.body)
                    # print('\n')

                    self.msg_buff = self.msg_buff[(message.size() + 1):]

                    yield message

    def send(self, message_body):
        self.send_lock.acquire()
        try:
            self.s.send(Packet(Message(message_body).to_text()).to_raw())
        finally:
            self.send_lock.release()
