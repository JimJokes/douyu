import socket
import threading
from chat.network.packet import Packet
from chat.network.message import Message

HOST = 'openbarrage.douyutv.com'
PORT = 8601

MAX_RECV_SIZE = 4096


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

                # print(self.buff)
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

                    self.msg_buff = self.msg_buff[(message.size() + 1):]

                    yield message

    def send(self, message_body):
        self.send_lock.acquire()
        try:
            self.s.send(Packet(Message(message_body).to_text()).to_raw())
        finally:
            self.send_lock.release()

    async def srv(self):

        while True:
            data = await self.s.recv(MAX_RECV_SIZE)
            if not data:
                continue
            await data
