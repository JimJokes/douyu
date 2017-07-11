import time
import logging
import threading
from queue import Empty

from message import Message
from packet import Packet
from utils import ReplyMessage

logger = logging.getLogger('main.'+__name__)
try:
    from client_test import Client
except ImportError:
    from client import Client

KEEP_ALIVE_INTERVAL_SECONDS = 45


class Data:
    def __init__(self):
        self.time = now_time()


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
        self.app = KeepAlive(self.client, KEEP_ALIVE_INTERVAL_SECONDS)
        self.alive = threading.Event()
        self.alive.set()

    def run(self):
        self._connect()
        self.keep_alive()
        while self.alive.is_set():
            try:
                self.gifts = self.gift_q.get(False)
            except Empty:
                pass
            message = self._receive()
            if message is None:
                continue
            else:
                self._handle_message(message)

    def _handle_message(self, message):
        data = Data()
        msg_type = message.attr('type')
        data.msg_type = msg_type
        data.nn = message.attr('nn')
        data.room = message.attr('rid')

        if msg_type == 'loginres':
            data.txt = self._join_group()

        elif msg_type == 'chatmsg':
            data.lv = message.attr('level')
            data.txt = message.attr('txt')

        elif msg_type == 'uenter':
            data.txt = '进入了直播间！'

        elif msg_type == 'dgb':
            gfid = message.attr('gfid')
            try:
                data.gift = self.gifts[gfid]
            except KeyError:
                data.gift = '未知礼物%s' % gfid
            data.dn = '主播'
            data.hits = message.attr('hits') or 1

        elif msg_type == 'bc_buy_deserve':
            data.nn = message.attr('sui')['nick']
            data.dn = '主播'
            data.gift = self.cq[message.attr('lev')]
            data.hits = message.attr('hits')

        elif msg_type == 'spbc':
            data.nn = message.attr('sn')
            data.gift = message.attr('gn')
            data.dn = message.attr('dn')
            data.room = message.attr('drid')
            data.hits = message.attr('gc')

        elif msg_type == 'ggbb':
            data.nn = message.attr('dnk')
            data.dn = message.attr('snk')
            data.gift = '鱼丸'
            data.num = message.attr('sl')

        elif msg_type == 'gpbc':
            data.nn = message.attr('dnk')
            data.dn = message.attr('snk')
            data.gift = message.attr('pnm')
            data.num = message.attr('cnt')

        self.result_q.put(data)
        try:
            self.root.event_generate('<<MESSAGE>>')
        except RuntimeError:
            pass

    def _receive(self):
        res = self.client.receive()

        if res.style == ReplyMessage.ERROR:
            self._logout()
            self.client.disconnect()
            self._connect()
            return None

        elif res.style == ReplyMessage.SUCCESS:
            data = res.data
            try:
                buff = data.decode()
                message = Message.sniff(buff)
                return message
            except UnicodeDecodeError as e:
                logger.info(e)
                logger.info(data)
                return None

    def _connect(self):
        num = 0
        data = {}
        while True:
            res = self.client.connect()

            if res.style == ReplyMessage.SUCCESS:
                self._login()
                break
            elif res.style == ReplyMessage.ERROR:
                if num < 30:
                    num += 1
                    continue
                else:
                    num = 0
                    data.msg_type = 'error'
                    data.txt = '弹幕服务器连接错误，请重新连接！'
                    self.result_q.put(data)
                    try:
                        self.root.event_generate('<<MESSAGE>>')
                    except RuntimeError:
                        pass

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
        self.client.send_msg(Packet(Message(data).to_text()).to_raw())

    def keep_alive(self):
        self.app.setDaemon(True)
        self.app.start()

    def quit(self):
        self.app.quit()
        self.alive.clear()
