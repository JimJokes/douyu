import os, io
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import struct
import webbrowser
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


class View(tk.Frame):

    def __init__(self, master=None):
        super(View, self).__init__(master)
        self.a = 0.5
        self.b = 0.5
        self.pack(padx=500, pady=300)
        self.window()

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
        win = Popup()
        win.mainloop()

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


class Popup(tk.Tk):
    def __init__(self, *args, **kwargs):
        super(Popup, self).__init__(*args, **kwargs)
        self.imageList = []
        self.attribute()
        self.alpha = 0
        self.position()
        self.window()
        self.fade_in()
        self.leave()

    def position(self):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        y = screen_height - 80 - 50
        x = screen_width - 420
        self.geometry('%sx%s+%s+%s' % (400, 80, x, y))

    def attribute(self):
        self.resizable(False, False)
        self.focusmodel('passive')
        self.attributes('-topmost', 1)
        self.overrideredirect(True)
        self.attributes('-alpha', 0)

    def window(self):
        frame = tk.Frame(self, bg='white')
        frame.place(relheight=1, relwidth=1)

        img = self.add_image()
        canvas = tk.Canvas(frame, bg='white')
        canvas.create_image(75, 40, image=img)
        canvas.place(relheight=1, relwidth=0.4)

        title = tk.Label(frame, text='今天不知道干嘛，聊天哈哈哈哈哈', bg='white', anchor=tk.NW)
        title.place(relheight=0.33, relwidth=0.7, relx=0.4)
        status = tk.Label(frame, text='直播中', bg='white', anchor=tk.NW)
        status.place(relheight=0.33, relwidth=0.7, relx=0.4, rely=0.33)
        name = tk.Label(frame, text='还哦啊浮雕', bg='white', anchor=tk.NW)
        name.place(relheight=0.33, relwidth=0.7, relx=0.4, rely=0.66)

        frame.bind('<Enter>', self.enter)
        frame.bind('<Leave>', self.leave)
        frame.bind_all('<Button-1>', self.open_browser)

    def add_image(self):
        url = 'https://rpic.douyucdn.cn/a1706/04/00/196_170604002259.jpg'
        with urlopen(url) as f:
            img_bytes = f.read()
        img = Image.open(io.BytesIO(img_bytes))
        width = img.width
        height = img.height
        f = min([150/width, 80/height])
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
        self.id = self.after(5000, self.fade_out)

    def open_browser(self, *args):
        webbrowser.open('www.baidu.com')

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
            self.imageList = []

if __name__ == '__main__':
    app = Popup()
    app.mainloop()
