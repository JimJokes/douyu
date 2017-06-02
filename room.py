import threading
import time

import logging
logger = logging.getLogger('main.'+__name__)
try:
    from client_test import Client
except ImportError:
    from client import Client

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
            print('发送心跳验证')
            currents_ts = int(time.time())
            self.client.send({
                'type': 'keeplive',
                'tick': currents_ts
            })
            time.sleep(self.delay)


class ChatRoom:
    channel_id = -9999

    def __init__(self, room_id):
        self.room_id = room_id
        self.client = Client()

    def connect(self):
        for mess in self.client.connect():
            yield mess

    def knock(self):
        try:
            self.client.send({'type': 'loginreq', 'roomid': self.room_id})
        except Exception as e:
            logger.exception(e)

        for message in self.client.receive():

            if not message:
                continue

            msg_type = message.attr('type')

            if msg_type == 'loginres':
                try:
                    self.client.send({'type': 'joingroup', 'rid': self.room_id, 'gid': self.channel_id})
                    logger.info('已连接到弹幕服务器，房间id：%s' % self.room_id)
                except Exception as e:
                    logger.exception(e)
            if msg_type == 'error':
                logger.warning('error:'+message.attr('code'))

            yield message

    def cutoff(self):
        self.client.send({'type': 'logout'})
        self.client.disconnect()
