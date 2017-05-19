import os
import tkinter as tk
import time, threading
from tkinter.messagebox import *

from tkinter.scrolledtext import *
from tkinter.constants import END

import re

from chat.network.utils import align_right
from chat.room import ChatRoom, KEEP_ALIVE_INTERVAL_SECONDS, KeepAlive

star_file = os.path.join(os.path.dirname(__file__), 'starList')
j = 0
i = 0
stars = []


def read_text():
    with open(star_file, 'r') as f:
        return f.readlines()


# todo: 整合窗口
class View(tk.Frame):
    def __init__(self, master=None):
        super(View, self).__init__(master)
        self.pack(padx=500, pady=300)
        self.window()

    def window(self):
        frame_left = tk.LabelFrame(text='全部弹幕：', padx=10, pady=10)
        frame_left.place(relwidth=0.5, relheight=1)

        self.text_damnu = ScrolledText(frame_left)
        self.text_damnu.place(relwidth=1, relheight=1)

        frame_right = tk.Frame(relief=tk.FLAT)
        frame_right.place(relwidth=0.5, relheight=1, relx=0.5)

        frame_star = tk.LabelFrame(frame_right, text='关注列表：(一行一个ID)', padx=10, pady=10)
        frame_star.place(relwidth=0.5, relheight=0.3)
        self.text_star = ScrolledText(frame_star)
        self.text_star.place(relwidth=0.8, relheight=1)
        self.read_stars()
        button_star = tk.Button(frame_star, text='确定', command=self.write_stars)
        button_star.place(anchor=tk.NE, relx=1, height=22, rely=0)

        frame_id = tk.Frame(frame_right, relief=tk.FLAT)
        frame_id.place(relwidth=0.5, relheight=0.1, rely=0.3)
        label_1 = tk.Label(frame_id, text='直播间ID：')
        label_1.place(anchor=tk.NE, relx=0.5, rely=0.1, height=17, relwidth=0.5)
        self.entry_id = tk.Entry(frame_id)
        self.entry_id.insert(tk.END, '196')
        self.entry_id.place(relx=0.5, rely=0.1, height=17, relwidth=0.4)
        self.button_start = tk.Button(frame_id, text='连接', command=self.on)
        self.button_start.place(anchor=tk.NE, relx=0.4, rely=0.6, width=55, height=22)
        self.button_stop = tk.Button(frame_id, text='断开连接', state=tk.DISABLED, command=self.off)
        self.button_stop.place(relx=0.6, rely=0.6, width=55, height=22)

        frame_info = tk.LabelFrame(frame_right, text='主播信息：')
        frame_info.place(relx=0.5, relwidth=0.5, relheight=0.4)

        frame_star_danmu = tk.LabelFrame(frame_right, text='关注内容：', padx=10, pady=10)
        frame_star_danmu.place(rely=0.4, relwidth=1, relheight=0.6)
        text_star_danmu = ScrolledText(frame_star_danmu)
        text_star_danmu.place(relwidth=1, relheight=1)

    def read_stars(self):
        if not os.path.exists(star_file):
            with open(star_file, 'w'):
                pass
        else:
            for line in read_text():
                self.text_star.insert(tk.END, line)

    def write_stars(self):
        text = self.text_star.get(1.0, tk.END)
        for line in text.split('\n'):
            if line.strip():
                stars.append(line.strip())
        with open(star_file, 'w') as f:
            f.write('\n'.join(stars))
        self.text_star.delete(1.0, tk.END)
        self.read_stars()

    def on(self):
        room_id = self.entry_id.get()
        if not re.match('\d+', room_id):
            showwarning('直播间ID不正确', '请输入正确的直播间ID！')
        else:
            self.dammu = Danmu(self.text_damnu, self.text_star, room_id)
            self.dammu.setDaemon(True)
            self.dammu.start()
            self.button_start['state'] = tk.DISABLED
            self.button_stop['state'] = tk.NORMAL

    def off(self):
        self.dammu.stop = True
        self.button_start['state'] = tk.NORMAL
        self.button_stop['state'] = tk.DISABLED


class Danmu(threading.Thread):
    def __init__(self, text, text_star, roomid):
        super(Danmu, self).__init__()
        self.text = text
        self.text_star = text_star
        self._roomid = roomid
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
                    if _uname in stars:
                        self.update_star(message)
                    self.update_dammu(message)

                if msg_type == 'uenter':
                    _uname = msg.attr('nn')
                    if _uname in stars:
                        message = '%s 进入了直播间！' % _uname
                        self.update_star(message)
                # elif msg_type == 'uenter':
                #     message = '%s [%s]:[%s][等级:%s] 进入了直播间!' % (now, rooms[_roomid], _uname, msg.attr('level'))
                #     yield message

            except KeyError:
                continue

    def update_dammu(self, message):
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


if __name__ == "__main__":
    root = View()
    root.master.title('斗鱼弹幕姬')
    root.master.minsize(height=300, width=500)
    root.mainloop()
