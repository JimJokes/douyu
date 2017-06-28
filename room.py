import threading
import time

import logging
logger = logging.getLogger('main.'+__name__)
try:
    from client_test import Client
except ImportError:
    from client import Client
from utils import ReplyMessage

RAW_BUFF_SIZE = 4096
KEEP_ALIVE_INTERVAL_SECONDS = 45


class KeepAlive(threading.Thread):
    def __init__(self, client, delay):
        super(KeepAlive, self).__init__()
        self.client = client
        self.delay = delay
        self.stop = False

    def run(self):
        while True:
            if self.stop:
                raise SystemExit
            # print('发送心跳验证')
            currents_ts = int(time.time())
            try:
                self.client.send_msg({
                    'type': 'keeplive',
                    'tick': currents_ts
                })
            except Exception as e:
                logger.exception(e)
            time.sleep(self.delay)


class ChatRoom(threading.Thread):
    channel_id = -9999

    def __init__(self, room, result_q):
        super(ChatRoom, self).__init__()
        self.room = room
        self.result_q = result_q
        self.client = Client()
        self.alive = threading.Event()
        self.alive.set()

    def run(self):
        self.connect()
        while self.alive:
            self.receive()

    def receive(self):
        res = self.client.receive()

        if res.type == ReplyMessage.ERROR:
            if res.code == 401:
                self.quit_group()
            self.client.disconnect()
            self.connect()

        elif res.type == ReplyMessage.SUCCESS:
            message = res.data

    def connect(self):
        while True:
            res = self.client.connect()

            if res.type == ReplyMessage.SUCCESS:
                break
            elif res.type == ReplyMessage.WARNING:
                res.code = 2000
                res.data = '弹幕服务器连接错误，请重新连接！'
                self.result_q.put(res)

            time.sleep(1)

    def join_group(self):
        data = {'type': 'joingroup', 'rid': self.room, 'gid': self.channel_id}
        res = self.client.send_msg(data)

        if res == ReplyMessage.SUCCESS:
            res.code = 2000
            res.data = '已连接到弹幕服务器，房间id：%s' % self.room
            self.result_q.put(res)

    def quit_group(self):
        data = {'type': 'logout'}
        self.client.send_msg(data)
