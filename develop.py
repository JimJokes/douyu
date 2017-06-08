import os, io
import tkinter as tk
from http.client import IncompleteRead
import threading
from tkinter.font import Font
from tkinter.scrolledtext import ScrolledText
import struct
import webbrowser
from urllib.error import URLError
from urllib.request import urlopen
import base64
import urllib

from PIL import ImageTk, Image
import time


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

    def __init__(self, master=None):
        super(View, self).__init__(master)
        self.a = 0.5
        self.b = 0.5
        self.window()
        self.win = Popup()

    def window(self):
        m = tk.PanedWindow()

        left = tk.LabelFrame(m, text='弹幕：', padx=10, pady=10)
        m.add(left)

        right = tk.Frame(m)
        m.add(right)

        m.place(relwidth=1, relheight=1)
        m.bind('<Button1-ButtonRelease>', lambda x: self.position(x, m, 0))
        m.bind('<Configure>', lambda x: self.resize(x, m, 0))

        danmu = ROSText(left, insertwidth=0)
        danmu.place(relwidth=1, relheight=1)
        danmu.insert(tk.END, 'ioafoi\nofja\nihfipahiafsifjia\nioafja\nfjioaiofhao')

        a = tk.PanedWindow(right, orient=tk.VERTICAL)

        top = tk.Frame()
        a.add(top)

        bottom = tk.LabelFrame(text='关注：', padx=10, pady=10)
        attention = ROSText(bottom, insertwidth=0)
        attention.place(relwidth=1, relheight=1)
        a.add(bottom)

        button = tk.Button(top, text='提醒', command=self.popup)
        button.place(relx=0.5, rely=0.5)

        a.place(relwidth=1, relheight=1)
        a.bind('<Button1-ButtonRelease>', lambda x: self.position(x, a, 1))
        a.bind('<Configure>', lambda x: self.resize(x, a, 1))
        self.update()
        m.sash_place(0, int(m.winfo_width()/2), 1)
        a.sash_place(0, 1, int(a.winfo_height()/2))

    def popup(self):
        url = 'https://rpic.douyucdn.cn/a1706/04/00/196_170604002259.jpg'
        title = '哦覅放假啊活动我还哦啊hi'
        live = 123
        name = '后返回骚的房间啊'
        self.win.name_text.set(name)
        self.win.status_text.set('直播中(已播%s分钟)' % live)
        self.win.title_text.set(title)
        self.win.image = url
        self.win.room_id = 196
        self.after(0, self.win.run)

    def position(self, event, entity, index):
        if entity.identify(event.x, event.y) == (0, 'sash'):
            if index == 0:
                self.a = entity.sash_coord(0)[0] / entity.winfo_reqwidth()
                # print(self.a)
            elif index == 1:
                self.b = entity.sash_coord(0)[1] / entity.winfo_reqheight()
                # print(self.b)

    def resize(self, event, entity, index):
        # entity = tk.PanedWindow()
        if index == 0:
            # print('a:'+str(self.a))
            entity.sash_place(0, int(event.width*self.a), 1)
        elif index == 1:
            # print('b:'+str(self.b))
            entity.sash_place(0, 1, int(event.height*self.b))


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

    def run(self):
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
        frame = tk.Frame(self, bg='white', cursor='hand2')
        frame.place(relheight=1, relwidth=1)

        self.frame_image = tk.Frame(frame, bg='white', bd=0)
        self.frame_image.place(relheight=1, relwidth=0.3)
        self.canvas = tk.Canvas(self.frame_image, bg='white', bd=0)
        self.canvas.place(relheight=1, relwidth=1)

        title_font = Font(size=11, family='microsoft yahei')
        self.title_text = tk.StringVar()
        title = tk.Label(frame, font=title_font, textvariable=self.title_text,
                         bg='white', bd=0, justify=tk.LEFT, anchor=tk.W)
        title.place(relheight=0.5, relwidth=0.7, relx=0.32)
        self.status_text = tk.StringVar()
        status = tk.Label(frame, textvariable=self.status_text, bg='white', anchor=tk.W, bd=0)
        status.place(relheight=0.2, relwidth=0.7, relx=0.32, rely=0.5)
        self.name_text = tk.StringVar()
        name = tk.Label(frame, textvariable=self.name_text, bg='white', anchor=tk.W, bd=0, fg='gray')
        name.place(relheight=0.3, relwidth=0.7, relx=0.32, rely=0.7)

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

        title.configure(wraplength=title.winfo_width()-45)

    def add_image(self, frame):
        while True:
            try:
                with urllib.request.urlopen(self.image) as f:
                    img_bytes = f.read()
                break
            except (IncompleteRead, URLError, ConnectionRefusedError, ConnectionResetError):
                time.sleep(1)
                continue
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
        self.id = self.after(10000, self.fade_out)

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
            self.destroy()
            # self.imageList = []

    def close(self, *args):
        self.destroy()


def a():
    i = 0
    while True:
        if i == 20:
            return
        else:
            yield i
            i += 1
            time.sleep(1)


def b():
    for i in a():
        yield i
    print('b.end')
    time.sleep(5)


if __name__ == '__main__':
    for i in b():
        print(i)
    print('end')
