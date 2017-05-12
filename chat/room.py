import time
import logging
import threading

from chat.network.client import Client

RAW_BUFF_SIZE = 4096
KEEP_ALIVE_INTERVAL_SECONDS = 45


def keep_alive(client, delay):
    while True:
        print('发送心跳验证')
        currents_ts = int(time.time())
        client.send({
            'type': 'keeplive',
            'tick': currents_ts
        })
        time.sleep(delay)


class ChatRoom:
    client = None
    room_id = None
    channel_id = -9999

    callbacks = {}

    def __init__(self, room_id):
        self.room_id = room_id
        self.client = Client()

    def on(self, event_name, callback):
        callback_list = None
        try:
            callback_list = self.callbacks[event_name]
        except KeyError:
            callback_list = []
            self.callbacks[event_name] = callback_list
        callback_list.append(callback)
        # print(self.callbacks)

    def trigger_callbacks(self, event_name, message):
        callback_list = None
        try:
            callback_list = self.callbacks[event_name]
        except KeyError:
            logging.info('Message of type "%s" is not handled' % event_name)
            return
        # print(callback_list)
        if callback_list is None or len(callback_list) <= 0:
            return

        for callback in callback_list:
            callback(message)

    def knock(self):
        try:
            print('发送登录申请')
            self.client.send({'type': 'loginreq', 'roomid': self.room_id})
        except Exception as e:
            print(e)
        app = threading.Thread(target=keep_alive, args=(self.client, KEEP_ALIVE_INTERVAL_SECONDS))
        # app.setDaemon(True)
        app.start()

        for message in self.client.receive():
            if not message:
                continue

            msg_type = message.attr('type')

            if msg_type == 'loginres':
                try:
                    self.client.send({'type': 'joingroup', 'rid': self.room_id, 'gid': self.channel_id})
                    print('已连接到弹幕服务器，房间id：%s' % self.room_id)
                except Exception as e:
                    print(e)
            if msg_type == 'error':
                print(message.attr('code'))

            # self.trigger_callbacks(msg_type, message)
            yield message
