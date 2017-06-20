import os, sys, io
import re
import tkinter as tk
import urllib.request
import webbrowser
from http.client import IncompleteRead
from tkinter.messagebox import *
from tkinter.scrolledtext import *
from tkinter.font import Font
from urllib.error import URLError

import time

import logging
from PIL import ImageTk, Image

from dammu import Danmu
from roomInfo import RoomInfo
import utils

logger = logging.getLogger('main.'+__name__)

if getattr(sys, 'frozen', False):
    star_file = os.path.join(os.getcwd(), 'starList.txt')
    icon = os.path.join(getattr(sys, '_MEIPASS', '.'), 'icon.ico')
else:
    star_file = os.path.join(os.path.dirname(__file__), 'starList.txt')
    icon = os.path.join(os.path.dirname(__file__), 'icon.ico')
# star_file = os.path.abspath('starList.txt')


def read_text():
    if not os.path.exists(star_file):
        with open(star_file, 'w', encoding='utf-8'):
            return []
    else:
        with open(star_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            return lines


def auto_wrap(event, entity):
    pad = int(str(entity['bd']))
    entity.configure(wraplength=event.width - pad * 2)


def resize(event, entity1, entity2):
    width = event.width-450
    entity1.configure(width=width)
    height = event.height-250
    entity2.configure(height=height)


class ROSText(ScrolledText):
    commandsToRemove = (
        "<Control-Key-h>",
        "<Meta-Key-Delete>",
        "<Meta-Key-BackSpace>",
        "<Meta-Key-d>",
        "<Meta-Key-b>",
        "<<Redo>>",
        "<<Undo>>",
        "<Control-Key-t>",
        "<Control-Key-o>",
        "<Control-Key-k>",
        "<Control-Key-d>",
        "<Key>",
        "<Key-Insert>",
        "<<PasteSelection>>",
        "<<Clear>>",
        "<<Paste>>",
        "<<Cut>>",
        "<Key-BackSpace>",
        "<Key-Delete>",
        "<Key-Return>",
        "<Control-Key-i>",
        "<Key-Tab>",
        "<Shift-Key-Tab>"
    )

    def __init__(self, *args, **kwargs):
        super(ROSText, self).__init__(*args, **kwargs)
        self._init_tag()

    def _init_tag(self):
        for key in self.bind_class('Text'):
            if key not in self.commandsToRemove:
                command = self.bind_class('Text', key)
                self.bind_class('ROSText', key, command)

        bind_tags = tuple(tag if tag != 'Text' else 'ROSText' for tag in self.bindtags())
        self.bindtags(bind_tags)


class View(tk.Tk):
    def __init__(self, width, height, *args, **kwargs):
        super(View, self).__init__(*args, **kwargs)
        self.width = width
        self.height = height
        self.icon()
        self.position()
        self.window()
        self.win = Popup()

    def icon(self):
        self.iconbitmap(icon)

    def position(self):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        size = '%sx%s+%s+%s' % (self.width, self.height,
                                int((screen_width-self.width)/2), int((screen_height-self.height)/2))
        self.geometry(size)

    def window(self):
        frame = tk.Frame()
        frame.place(relwidth=1, relheight=1)

        frame_left = tk.LabelFrame(frame, text='弹幕：', padx=10, pady=10)
        frame_left.place(relheight=1)

        font = Font(size=12)
        self.text_danmu = ROSText(frame_left, font=font, spacing1=5, insertwidth=0)
        self.text_danmu.place(relwidth=1, relheight=1)

        frame_right = tk.Frame(frame)
        frame_right.place(anchor=tk.NE, width=450, relheight=1, relx=1)

        frame_info = tk.Frame(frame_right)
        frame_info.place(relwidth=1, height=250)

        frame_star = tk.LabelFrame(frame_info, text='关注列表：(一行一个ID)', padx=10, pady=10)
        frame_star.place(relwidth=0.5, relheight=0.75)
        self.text_star = ScrolledText(frame_star)
        self.text_star.place(relwidth=0.8, relheight=1)
        self.read_stars()
        button_star = tk.Button(frame_star, text='保存', command=self.write_stars)
        button_star.place(anchor=tk.NE, relx=1, height=22, rely=0)
        button_refresh = tk.Button(frame_star, text='更新', command=self.read_stars)
        button_refresh.place(anchor=tk.NE, relx=1, height=22, rely=0.2)
        self.lock_text = tk.StringVar()
        lock = tk.Button(frame_star, textvariable=self.lock_text, command=self.lock)
        self.lock_text.set('锁屏')
        lock.place(anchor=tk.SE, relx=1, height=22, rely=1)

        frame_id = tk.Frame(frame_info)
        frame_id.place(relwidth=0.5, relheight=0.25, rely=0.75)
        label = tk.Label(frame_id, text='直播间ID：')
        label.place(anchor=tk.NE, relx=0.5, rely=0.1, height=17, relwidth=0.5)
        self.entry_id = tk.Entry(frame_id)
        self.entry_id.insert(tk.END, '196')
        self.entry_id.place(relx=0.5, rely=0.1, height=17, relwidth=0.4)
        self.button_start = tk.Button(frame_id, text='连接', command=self.on)
        self.button_start.place(anchor=tk.NE, relx=0.4, rely=0.6, width=55, height=22)
        self.button_stop = tk.Button(frame_id, text='断开连接', state=tk.DISABLED, command=self.off)
        self.button_stop.place(relx=0.6, rely=0.6, width=55, height=22)
        self.room_info(frame_info)

        frame_star_danmu = tk.LabelFrame(frame_right, text='关注：', padx=10, pady=10)
        frame_star_danmu.place(anchor=tk.SE, rely=1, relx=1, relwidth=1)
        self.text_star_danmu = ROSText(frame_star_danmu, font=font, spacing1=5, insertwidth=0)
        self.text_star_danmu.place(relwidth=1, relheight=1)
        frame.bind('<Configure>', lambda x: resize(x, frame_left, frame_star_danmu))

    def lock(self):
        if utils.CheckVar:
            utils.CheckVar = False
            self.lock_text.set('滚屏')
        else:
            utils.CheckVar = True
            self.lock_text.set('锁屏')

    def room_info(self, frame):
        self.frame_info = tk.LabelFrame(frame, text='主播信息：')
        self.frame_info.place(relx=0.5, relwidth=0.5, relheight=1)

        str_1 = self.msg('直播间标题：', 0, relheight=0.2)
        str_2 = self.msg('主播：', 0.2)
        str_3 = self.msg('开播状态：', 0.3)
        str_4 = self.msg('关注：', 0.4)
        str_5 = self.msg('体重：', 0.5)
        str_6 = self.msg('人气：', 0.6)
        str_7 = self.msg('上次直播：', 0.7)
        str_8 = self.msg('更新时间：', 0.8)
        self.string = (str_1, str_2, str_3, str_4, str_5, str_6, str_7, str_8)

    def on(self):
        room_id = self.entry_id.get()
        if not re.match('\d+', room_id):
            showwarning('直播间ID不正确', '请输入正确的直播间ID！')
        else:
            self.danmu = Danmu(self.text_danmu, self.text_star_danmu, room_id)
            self.danmu.setDaemon(True)

            if room_id != utils.room:
                self.danmu.delete_danmu()
                utils.room = room_id
            self.danmu.start()
            self.button_start['state'] = tk.DISABLED
            self.button_stop['state'] = tk.NORMAL
            self.update_info(room_id)

    def off(self):
        self.danmu.stop = True
        self.info.stop = True
        self.button_start['state'] = tk.NORMAL
        self.button_stop['state'] = tk.DISABLED
        # print(threading.enumerate())

    def update_info(self, room_id):
        self.info = RoomInfo(room_id, self.win, *self.string)
        self.info.setDaemon(True)
        self.info.start()

    def read_stars(self):
        utils.stars = []
        self.text_star.delete(1.0, tk.END)
        for line in read_text():
            utils.stars.append(line.strip())
            self.text_star.insert(tk.END, line)
        # print(utils.stars)

    def write_stars(self):
        text = self.text_star.get(1.0, tk.END)
        with open(star_file, 'w', encoding='utf-8') as f:
            for line in text.split('\n'):
                if line.strip():
                    f.write(line.strip()+'\n')
        self.text_star_danmu.insert(tk.END, '关注成功！\n')
        if utils.CheckVar:
            self.text_star_danmu.see(tk.END)
        self.read_stars()

    def msg(self, text, rely, relheight=None):
        string = tk.StringVar()
        label = tk.Label(self.frame_info, text=text, anchor=tk.NW)
        label.place(anchor=tk.NE, relx=0.4, rely=rely, relwidth=0.35)
        label.bind('<Configure>', lambda x: auto_wrap(x, label))
        msg = tk.Label(self.frame_info, anchor=tk.NW, justify=tk.LEFT, textvariable=string)
        msg.place(relx=0.4, rely=rely, relwidth=0.55, relheight=relheight)
        msg.bind('<Configure>', lambda x: auto_wrap(x, msg))
        return string


class Popup(tk.Toplevel):
    def __init__(self, image=None, room_id=None, *args, **kwargs):
        super(Popup, self).__init__(*args, **kwargs)
        self.image = image
        self.room_id = room_id
        self.imageList = []
        self.attribute()
        self.alpha = 0
        self.position()
        self.window()

    def pop_up(self):
        img = self.add_image(self.frame_image)
        height = self.canvas.winfo_height()
        width = self.canvas.winfo_width()
        self.canvas.create_image(int(width/2), int(height/2), image=img)

        self.fade_in()
        self.leave()

    def position(self):
        self.geometry('%sx%s-%s-%s' % (400, 90, 20, 50))

    def attribute(self):
        self.resizable(False, False)
        self.focusmodel('passive')
        self.attributes('-topmost', 1)
        self.overrideredirect(True)
        self.attributes('-alpha', 0)

    def window(self):
        frame = tk.Frame(self, bg='white', cursor='hand2', relief=tk.RAISED, bd=3)
        frame.place(relheight=1, relwidth=1)

        self.frame_image = tk.Frame(frame, bg='white', bd=0)
        self.frame_image.place(relheight=1, relwidth=0.3)
        self.canvas = tk.Canvas(self.frame_image, bg='white', bd=0)
        self.canvas.place(relheight=1, relwidth=1)

        title_font = Font(size=11, family='microsoft yahei')
        self.title_text = tk.StringVar()
        title = tk.Label(frame, font=title_font, textvariable=self.title_text,
                         bg='white', bd=0, justify=tk.LEFT, anchor=tk.W)
        title.place(relheight=0.5, relwidth=0.65, relx=0.32)
        self.status_text = tk.StringVar()
        status = tk.Label(frame, textvariable=self.status_text, bg='white', anchor=tk.W, bd=0)
        status.place(relheight=0.2, relwidth=0.65, relx=0.32, rely=0.5)
        self.name_text = tk.StringVar()
        name = tk.Label(frame, textvariable=self.name_text, bg='white', anchor=tk.W, bd=0, fg='gray')
        name.place(relheight=0.3, relwidth=0.65, relx=0.32, rely=0.7)

        close = tk.Label(frame, text='X', cursor='arrow', bg='white')
        close.place(anchor=tk.NE, width=30, height=30, relx=1, rely=0)

        frame.bind('<Enter>', self.enter)
        frame.bind('<Leave>', self.leave)
        frame.bind('<Button-1>', self.open_browser)
        self.frame_image.bind('<Button-1>', self.open_browser)
        self.canvas.bind('<Button-1>', self.open_browser)
        title.bind('<Button-1>', self.open_browser)
        status.bind('<Button-1>', self.open_browser)
        name.bind('<Button-1>', self.open_browser)
        close.bind('<Button-1>', self.close)

        self.update()

        title.configure(wraplength=title.winfo_width()-20)

    def add_image(self, frame):
        while True:
            try:
                with urllib.request.urlopen(self.image) as f:
                    img_bytes = f.read()
                break
            except (IncompleteRead, URLError, ConnectionRefusedError, ConnectionResetError):
                time.sleep(1)
                continue
            except Exception as e1:
                logger.exception(e1)
        img = Image.open(io.BytesIO(img_bytes))
        width = img.width
        height = img.height
        f = min(frame.winfo_width()/width, frame.winfo_height()/height)
        width = int(width*f)
        height = int(height*f)
        img = img.resize((width, height), Image.ANTIALIAS)
        img = ImageTk.PhotoImage(img)
        self.imageList.append(img)
        return img

    def enter(self, *args):
        self.after_cancel(self.id)
        self.attributes('-alpha', 1)
        self.alpha = 1

    def leave(self, *args):
        self.id = self.after(8000, self.fade_out)

    def open_browser(self, *args):
        webbrowser.open('www.douyu.com/%s' % self.room_id)

    def fade_in(self):
        if self.alpha < 1:
            self.alpha += 0.3
            self.attributes('-alpha', self.alpha)
            self.after(100, self.fade_in)
        else:
            self.attributes('-alpha', 1)

    def fade_out(self):
        if self.alpha > 0:
            self.alpha -= 0.2
            self.attributes('-alpha', self.alpha)
            self.id = self.after(100, self.fade_out)
        else:
            self.attributes('-alpha', 0)
            self.alpha = 0

    def close(self, *args):
        self.attributes('-alpha', 0)
        self.alpha = 0

