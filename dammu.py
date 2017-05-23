import threading
import time
from tkinter import END

from utils import align_right
from room import ChatRoom, KeepAlive, KEEP_ALIVE_INTERVAL_SECONDS

j = 0
i = 0


class Danmu(threading.Thread):
    def __init__(self, text, text_star, roomid, stars):
        super(Danmu, self).__init__()
        self.text = text
        self.text_star = text_star
        self._roomid = roomid
        self.stars = stars
        self.stop = False

    def run(self):
        _room = ChatRoom(self._roomid)
        app = KeepAlive(_room.client, KEEP_ALIVE_INTERVAL_SECONDS)
        app.setDaemon(True)
        app.start()

        self.text.insert(END, '开始监控[%s]的直播间弹幕！\n' % self._roomid)
        for msg in _room.knock():
            if self.stop:
                # _room.stop = True
                app.stop = True
                raise SystemExit
            try:
                msg_type = msg.attr('type')
                now = time.strftime("%y-%m-%d %H:%M:%S", time.localtime())
                _roomid = msg.attr('rid')

                if msg_type == 'chatmsg':
                    _ct = msg.attr('ct')
                    if _ct is None:
                        _ct = '网页'
                    else:
                        _ct = '手机'
                    _uname = msg.attr('nn')
                    message = align_right('[%s] %s' % (_ct, _uname), 25) + ':%s' % msg.attr('txt')
                    if _uname in self.stars:
                        self.update_star(message)
                    self.update_danmu(message)

                if msg_type == 'uenter':
                    _uname = msg.attr('nn')
                    if _uname in self.stars:
                        message = '%s 进入了直播间！' % _uname
                        self.update_star(message)
                # elif msg_type == 'uenter':
                #     message = '%s [%s]:[%s][等级:%s] 进入了直播间!' % (now, rooms[_roomid], _uname, msg.attr('level'))
                #     yield message

            except KeyError:
                continue

    def update_danmu(self, message):
        global j
        y = self.text.vbar.get()[1]
        self.text.insert(END, message + '\n')
        if j > 2999:
            self.text.delete(1.0, 2.0)
        else:
            j += 1
        if y == 1.0:
            self.text.see(END)

    def update_star(self, message):
        global i
        x = self.text_star.vbar.get()[1]
        self.text_star.insert(END, message + '\n')
        if i > 999:
            self.text_star.delete(1.0, 2.0)
        else:
            i += 1
        if x == 1.0:
            self.text_star.see(END)

    def delete_danmu(self):
        global j
        self.text.delete(1.0, END)
        j = 0
