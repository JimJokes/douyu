import threading
from tkinter import END
from tkinter.messagebox import askyesnocancel

import utils
from room import ChatRoom, KeepAlive, KEEP_ALIVE_INTERVAL_SECONDS


class Danmu(threading.Thread):
    def __init__(self, text, text_star, roomid, on, off):
        super(Danmu, self).__init__()
        self.text = text
        self.text_star = text_star
        self._roomid = roomid
        self.stop = False
        self.on = on
        self.off = off

    def run(self):
        _room = ChatRoom(self._roomid)
        app = KeepAlive(_room.client, KEEP_ALIVE_INTERVAL_SECONDS)
        app.setDaemon(True)
        app.start()

        self.text.insert(END, '开始监控[%s]的直播间弹幕！\n' % self._roomid)
        try:
            for msg in _room.knock():
                if self.stop:
                    app.stop = True
                    raise SystemExit
                try:
                    msg_type = msg.attr('type')

                    if msg_type == 'chatmsg':
                        # _ct = msg.attr('ct')
                        # if _ct is None:
                        #     _ct = '网页'
                        # else:
                        #     _ct = '手机'
                        _uname = msg.attr('nn')
                        _lv = msg.attr('level')
                        message = utils.align_right('[LV:%s] ' % _lv, 9) + utils.align_right('%s' % _uname, 21) + ':%s' % msg.attr('txt')
                        if _uname in utils.stars:
                            self.update_star(message)
                        self.update_danmu(message)

                    if msg_type == 'uenter':
                        _uname = msg.attr('nn')
                        if _uname in utils.stars:
                            message = '%s 进入了直播间！' % _uname
                            self.update_star(message)

                except KeyError:
                    continue
        except ConnectionError:
            self.off()
            flag = askyesnocancel('弹幕服务器连接失败', '是否重新连接弹幕服务器？')
            if flag:
                self.on()
            raise SystemExit

    def update_danmu(self, message):
        self.text.insert(END, message + '\n')
        if utils.j > 2999:
            self.text.delete(1.0, 2.0)
        else:
            utils.j += 1
        if utils.CheckVar:
            self.text.see(END)

    def update_star(self, message):
        self.text_star.insert(END, message + '\n')
        if utils.i > 999:
            self.text_star.delete(1.0, 2.0)
        else:
            utils.i += 1
        if utils.CheckVar:
            self.text_star.see(END)

    def delete_danmu(self):
        self.text.delete(1.0, END)
        utils.j = 0
