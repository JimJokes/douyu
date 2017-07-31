import time
import logging
import threading
from queue import Empty

from message import Message
from utils import ReplyMessage

logger = logging.getLogger('main.'+__name__)
try:
    from client_test import Client
except ImportError:
    from client import Client

KEEP_ALIVE_INTERVAL_SECONDS = 45


class KeepAlive(threading.Thread):
    def __init__(self, client, delay):
        super(KeepAlive, self).__init__()
        self.client = client
        self.delay = delay
        self.alive = threading.Event()
        self.alive.set()

    def run(self):
        while self.alive.is_set():
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

    def quit(self):
        self.alive.clear()


def now_time():
    return time.strftime('%m-%d %H:%M:%S', time.localtime())


class ChatRoom(threading.Thread):
    channel_id = -9999
    cq = {
        '1': '初级酬勤',
        '2': '中级酬勤',
        '3': '高级酬勤',
    }
    gifts = {}

    def __init__(self, room, result_q, gift_q, root):
        super(ChatRoom, self).__init__()
        self.room = room
        self.result_q = result_q
        self.gift_q = gift_q
        self.root = root
        self.client = Client()
        self.alive = threading.Event()
        self.alive.set()

    def run(self):
        self._connect()
        while self.alive.is_set():
            try:
                self.gifts = self.gift_q.get(False)
            except Empty:
                pass
            message = self._receive()
            if message is None:
                continue
            else:
                data = self._handle_message(message)
                if data:
                    self.result_put(data)
                else:
                    continue
        self._logout()

    def _handle_message(self, message):
        # print(message.body)
        message.set_attr('time', now_time())
        msg_type = message.attr('type')
        if msg_type == 'error':
            logger.error(message.body)
            return None

        elif msg_type == 'loginres':
            message.set_attr('txt', self._join_group())
            return message

        elif msg_type == 'chatmsg':
            return message

        elif msg_type == 'uenter':
            message.set_attr('txt', '进入直播间！')
            return message

        elif msg_type == 'dgb':
            gfid = message.attr('gfid')
            try:
                gift = self.gifts[gfid]
            except KeyError:
                gift = '未知礼物%s' % gfid
            message.set_attr('gift', gift)
            message.set_attr('room', message.attr('rid'))
            message.set_attr('dn', '主播')
            message.set_attr('hits', message.attr('hits') or 1)
            return message

        elif msg_type == 'bc_buy_deserve':
            message.set_attr('nn', message.attr('sui')['nick'])
            message.set_attr('room', message.attr('rid'))
            message.set_attr('dn', '主播')
            message.set_attr('gift', self.cq[message.attr('lev')])
            message.set_attr('hits', message.attr('hits') or 1)
            return message

        elif msg_type == 'spbc':
            message.set_attr('nn', message.attr('sn'))
            message.set_attr('gift', message.attr('gn'))
            message.set_attr('room', message.attr('drid'))
            message.set_attr('hits', message.attr('gc'))
            return message

        elif msg_type == 'ggbb':
            message.set_attr('gift', '鱼丸')
            message.set_attr('num', message.attr('sl'))
            return message

        elif msg_type == 'gpbc':
            message.set_attr('gift', message.attr('pnm'))
            message.set_attr('num', message.attr('cnt'))
            return message

        else:
            return None

    def result_put(self, data):
        self.result_q.put(data)
        try:
            self.root.event_generate('<<MESSAGE>>')
        except RuntimeError:
            pass

    def _receive(self):
        res = self.client.receive()

        if res.style == ReplyMessage.ERROR:
            self._logout()
            self._connect()
            return None

        elif res.style == ReplyMessage.SUCCESS:
            data = res.data
            try:
                buff = data.decode(errors='replace')
                message = Message.sniff(buff)
                # if message.attr('type') == 'chatmsg':
                #     print(message.body)
                return message
            except UnicodeDecodeError as e:
                logger.info(e)
                logger.info(data)
                return None

    def _connect(self):
        num = 0
        message = Message({})
        while True:
            res = self.client.connect()

            if res.style == ReplyMessage.SUCCESS:
                self._login()
                self.keep_alive()
                break
            elif res.style == ReplyMessage.ERROR:
                if num < 30:
                    num += 1
                    continue
                else:
                    num = 0
                    message.set_attr('type', 'con_error')
                    message.set_attr('txt', '弹幕服务器连接错误，请重新连接！')
                    self.result_put(message)

            time.sleep(1)

    def _login(self):
        data = {'type': 'loginreq', 'roomid': self.room}
        self.client.send_msg(data)

    def _join_group(self):
        data = {'type': 'joingroup', 'rid': self.room, 'gid': self.channel_id}
        res = self.client.send_msg(data)

        if res.style == ReplyMessage.SUCCESS:
            return '已连接到弹幕服务器，房间id：%s' % self.room

    def _logout(self):
        data = {'type': 'logout'}
        self.client.send_msg(data)
        self.app.quit()
        self.client.disconnect()

    def keep_alive(self):
        self.app = KeepAlive(self.client, KEEP_ALIVE_INTERVAL_SECONDS)
        self.app.setDaemon(True)
        self.app.start()

    def quit(self):
        self.alive.clear()
