import threading
import time

import logging

import utils
from message import Message
from packet import Packet

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
    cq = {
        '1': '初级酬勤',
        '2': '中级酬勤',
        '3': '高级酬勤',
    }

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
            message = self.receive()
            if message is None:
                continue
            else:
                self._handle_message(message)

    def _handle_message(self, message):
        data = {}
        msg_type = message.attr('type')
        data['time'] = self.now_time()
        data['type'] = msg_type
        if msg_type == 'chatmsg':
            data['nn'] = message.attr('nn')
            data['lv'] = message.attr('level')
            data['txt'] = message.attr('txt')

        elif msg_type == 'uenter':
            data['nn'] = message.attr('nn')
            data['txt'] = '进入了直播间！'

        elif msg_type == 'dgb':
            data['nn'] = message.attr('nn')
            gfid = message.attr('gfid')
            try:
                data['gift'] = utils.gifts[gfid]
            except KeyError:
                data['gift'] = '未知礼物%s' % gfid
            data['hit'] = message.attr('hits') or 1

        elif msg_type == 'bc_buy_deserve':
            data['nn'] = message.attr('sui')['nick']
            data['cp'] = self.cq[message.attr('lev')]
            data['hit'] = message.attr('hits')

        elif msg_type == 'spbc':
            data['nn'] = message.attr('sn')
            data['gift'] = message.attr('gn')
            data['dn'] = message.attr('dn')
            data['room'] = message.attr('drid')

        self.result_q.put(data)

    def now_time(self):
        return time.strftime('%m-%d %H:%M:%S', time.localtime())

    def receive(self):
        res = self.client.receive()

        if res.type == ReplyMessage.ERROR:
            if res.code == 401 or 402:
                self.quit_group()
            self.client.disconnect()
            self.connect()

        elif res.type == ReplyMessage.SUCCESS:
            data = res.data
            try:
                buff = data.decode()
                message = Message.sniff(buff)
                return message
            except UnicodeDecodeError as e:
                logger.info(e)
                logger.info(data)
                return None

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
        res = self.client.send_msg(Packet(Message(data).to_text()).to_raw())

        if res == ReplyMessage.SUCCESS:
            res.code = 2000
            res.data = '已连接到弹幕服务器，房间id：%s' % self.room
            self.result_q.put(res)

    def quit_group(self):
        data = {'type': 'logout'}
        self.client.send_msg(Packet(Message(data).to_text()).to_raw())

    def quit(self):
        self.alive.clear()

    def _reply(self, code=None, data=None):
        return ReplyMessage(ReplyMessage.SUCCESS, code, data)
