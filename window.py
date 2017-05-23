import os
import re
import tkinter as tk
from tkinter.messagebox import *
from tkinter.scrolledtext import *

from dammu import Danmu
from roomInfo import RoomInfo

star_file = os.path.join(os.path.dirname(__file__), 'starList.txt')
room = None
stars = []


def read_text():
    if not os.path.exists(star_file):
        with open(star_file, 'w', encoding='utf-8'):
            return []
    else:
        with open(star_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            return lines


def auto_wrap(event, entry):
    pad = int(str(entry['bd']))
    entry.configure(wraplength=event.width-pad*2)


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
        self.text_damnu.bind('<KeyPress>', lambda e: 'break')

        self.frame_right = tk.Frame(relief=tk.FLAT)
        self.frame_right.place(relwidth=0.5, relheight=1, relx=0.5)

        frame_star = tk.LabelFrame(self.frame_right, text='关注列表：(一行一个ID)', padx=10, pady=10)
        frame_star.place(relwidth=0.5, relheight=0.3)
        self.text_star = ScrolledText(frame_star)
        self.text_star.place(relwidth=0.8, relheight=1)
        self.read_stars()
        button_star = tk.Button(frame_star, text='确定', command=self.write_stars)
        button_star.place(anchor=tk.NE, relx=1, height=22, rely=0)

        frame_id = tk.Frame(self.frame_right, relief=tk.FLAT)
        frame_id.place(relwidth=0.5, relheight=0.1, rely=0.3)
        label = tk.Label(frame_id, text='直播间ID：')
        label.place(anchor=tk.NE, relx=0.5, rely=0.1, height=17, relwidth=0.5)
        self.entry_id = tk.Entry(frame_id)
        self.entry_id.insert(tk.END, '196')
        self.entry_id.place(relx=0.5, rely=0.1, height=17, relwidth=0.4)
        self.button_start = tk.Button(frame_id, text='连接', command=self.on)
        self.button_start.place(anchor=tk.NE, relx=0.4, rely=0.6, width=55, height=22)
        self.button_stop = tk.Button(frame_id, text='断开连接', state=tk.DISABLED, command=self.off)
        self.button_stop.place(relx=0.6, rely=0.6, width=55, height=22)
        self.room_info()

        frame_star_danmu = tk.LabelFrame(self.frame_right, text='关注内容：', padx=10, pady=10)
        frame_star_danmu.place(rely=0.4, relwidth=1, relheight=0.6)
        self.text_star_danmu = ScrolledText(frame_star_danmu)
        self.text_star_danmu.place(relwidth=1, relheight=1)
        self.text_star_danmu.bind('<KeyPress>', lambda e: 'break')

    def room_info(self):
        self.frame_info = tk.LabelFrame(self.frame_right, text='主播信息：')
        self.frame_info.place(relx=0.5, relwidth=0.5, relheight=0.4)

        self.str_1 = self.msg('直播间标题：', 0, relheight=0.2)
        self.str_2 = self.msg('主播：', 0.2)
        self.str_3 = self.msg('开播状态：', 0.3)
        self.str_4 = self.msg('关注：', 0.4)
        self.str_5 = self.msg('体重：', 0.5)
        self.str_6 = self.msg('人气：', 0.6)
        self.str_7 = self.msg('上次直播：', 0.7)
        self.str_8 = self.msg('上次更新：', 0.8)

    def on(self):
        global stars
        room_id = self.entry_id.get()
        if not re.match('\d+', room_id):
            showwarning('直播间ID不正确', '请输入正确的直播间ID！')
        else:
            self.danmu = Danmu(self.text_damnu, self.text_star_danmu, room_id, stars)
            self.danmu.setDaemon(True)
            if room_id != room:
                self.danmu.delete_danmu()
            self.danmu.start()
            self.button_start['state'] = tk.DISABLED
            self.button_stop['state'] = tk.NORMAL
            self.update_info(room_id)

    def off(self):
        self.danmu.stop = True
        self.info.stop = True
        self.button_start['state'] = tk.NORMAL
        self.button_stop['state'] = tk.DISABLED

    def update_info(self, room_id):
        string = (self.str_1, self.str_2, self.str_3, self.str_4, self.str_5, self.str_6, self.str_7, self.str_8)
        self.info = RoomInfo(room_id, *string)
        self.info.setDaemon(True)
        self.info.start()

    def read_stars(self):
        for line in read_text():
            self.text_star.insert(tk.END, line)

    def write_stars(self):
        global stars
        stars = []
        text = self.text_star.get(1.0, tk.END)
        for line in text.split('\n'):
            if line.strip():
                stars.append(line.strip())
        with open(star_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(stars))
            self.text_star_danmu.insert(tk.END, '关注成功！\n')
        self.text_star.delete(1.0, tk.END)
        self.read_stars()
        try:
            self.danmu.stars = stars
        except:
            pass

    def msg(self, text, rely, relheight=None):
        string = tk.StringVar()
        label = tk.Label(self.frame_info, text=text, anchor=tk.NW)
        label.place(anchor=tk.NE, relx=0.4, rely=rely, relwidth=0.35)
        label.bind('<Configure>', lambda x: auto_wrap(x, label))
        msg = tk.Label(self.frame_info, anchor=tk.NW, justify=tk.LEFT, textvariable=string)
        msg.place(relx=0.4, rely=rely, relwidth=0.55, relheight=relheight)
        msg.bind('<Configure>', lambda x: auto_wrap(x, msg))
        return string
