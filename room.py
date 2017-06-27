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


class ChatRoom:
    channel_id = -9999

    def __init__(self, room):
        self.room = room
        self.client = Client()
