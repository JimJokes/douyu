import os
import re
import requests
import tkinter as tk
from tkinter import ttk
from tkinter.font import Font

from PIL import ImageTk, Image
from utils import deserialize
from message import Message
from utils import lv, color, noble, color_cq, width_cq, bandage

pattern = re.compile(r'\[emot:dy([0-9]+)]')
code_pattern = re.compile(r'^\\xed\\\w{3}\\\w{3}$')


class ROSText(tk.Text):
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


data = 'type@=chatmsg/rid@=196/ct@=2/uid@=3298253/nn@=Akkyon/txt@=有几率/cid@=ca5d84a7ad444ef2f233020000000000/ic@=avanew@Sface@S201703@S27@S20@Sd418b2caf0bceee5897907bf2d4491d6/level@=63/sahf@=0/nl@=4/nc@=1/rg@=4/dlv@=3/dc@=73/bdlv@=3/bnn@=耀西/bl@=10/brid@=74751/hc@=e782738ead01e0978d3f351801f920f2/el@=eid@AA=1500000002@ASetp@AA=1@ASsc@AA=1@ASef@AA=0@AS@Seid@AA=1500000003@ASetp@AA=1@ASsc@AA=1@ASef@AA=0@AS@Seid@AA=1500000004@ASetp@AA=1@ASsc@AA=1@ASef@AA=0@AS@Seid@AA=1500000005@ASetp@AA=1@ASsc@AA=1@ASef@AA=0@AS@Seid@AA=1500000113@ASetp@AA=1@ASsc@AA=1@ASef@AA=0@AS@Seid@AA=1500000157@ASetp@AA=1@ASsc@AA=1@ASef@AA=0@AS@S/'


class Text(ROSText):
    def __init__(self, master, static_img, lv_img,
                 face_img, *args, **kwargs):
        super(Text, self).__init__(master, *args, **kwargs)
        self.static_img = static_img
        self.lv_img = lv_img
        self.face_img = face_img
        self.add_tag()

    def add_tag(self):
        self.tag_config('anchor', background='yellow')
        self.tag_config('red_name', foreground='#f03')
        self.tag_config('gold_name', foreground='gold')
        self.tag_config('name', foreground='#2b94ff')
        self.tag_config('col', foreground='#555')
        self.tag_config('col_1', foreground='#ff0000')
        self.tag_config('col_2', foreground='#1e87f0')
        self.tag_config('col_3', foreground='#7ac84b')
        self.tag_config('col_4', foreground='#ff7f00')
        self.tag_config('col_5', foreground='#9b39f4')
        self.tag_config('col_6', foreground='#ff69b4')

    def handle_message(self, message, tag=None):
        name = message.attr('nn')
        idx1 = self.index(tk.INSERT)
        self.handle_role(message)
        self.handle_noble(message)
        self.handle_cq(message, tag)
        self.handle_madel(message)
        self.handle_bandge(message, tag)
        self.handle_level(message)
        self.handle_name(message, name)
        self.handle_text(message)
        idx2 = self.index(tk.INSERT)
        if tag:
            self.tag_add('anchor', idx1, idx2)

    def handle_role(self, msg):
        role = None
        if msg.attr('pg') in ('5', '2') and msg.attr('sahf') == '1':
            role = 'super_admin'
        elif msg.attr('rg') == '4':
            role = 'roomadmin'
        elif msg.attr('rg') == '5':
            role = 'anchor'
        if role:
            self.image_create(tk.END, image=self.static_img['%s.png' % role])
            # self.insert(tk.END, ' ')

    def handle_noble(self, msg):
        nl = msg.attr('nl')
        if nl:
            self.image_create(tk.END, image=self.static_img[noble[nl]])
            # self.insert(tk.END, ' ')

    def handle_cq(self, msg, tag):
        dlv = msg.attr('dlv')
        dc = msg.attr('dc')
        bdlv = msg.attr('bdlv')
        if dlv and dc and int(dlv) > 0 and int(dc) > 0:
            self.window_create(tk.END, window=self.cq(dlv, dc, tag))
            # self.insert(tk.END, ' ')
        elif bdlv and int(bdlv) > 0:
            self.image_create(tk.END, image=self.static_img['cq_other.png'])
            # self.insert(tk.END, ' ')

    def handle_madel(self, msg):
        el = msg.attr('el')
        for item in el:
            if item['eid'] == '1500000005':
                self.image_create(tk.END, image=self.static_img['madel-s1.png'])
                # self.insert(tk.END, ' ')
            elif item['eid'] == '1500000003':
                self.image_create(tk.END, image=self.static_img['madel-s2.png'])
                # self.insert(tk.END, ' ')
            elif item['eid'] == '1500000002':
                self.image_create(tk.END, image=self.static_img['madel-s3.png'])
                # self.insert(tk.END, ' ')
            elif item['eid'] == '1500000160':
                self.image_create(tk.END, image=self.static_img['firstpay-award-icon.png'])
                # self.insert(tk.END, ' ')

    def handle_bandge(self, msg, tag):
        bnn = msg.attr('bnn')
        bl = msg.attr('bl')
        if bnn and bl:
            self.window_create(tk.END, window=self.bandge(bl, bnn, tag))
            # self.insert(tk.END, ' ')

    def handle_level(self, msg):
        ol = msg.attr('ol')
        level = msg.attr('level')
        if ol and int(ol) > 0:
            self.image_create(tk.END, image=self.lv_img['anchorLV%s.png' % ol])
            # self.insert(tk.END, ' ')
        elif level and int(level) > 0:
            self.image_create(tk.END, image=self.lv_img[lv[int(level)]])
            # self.insert(tk.END, ' ')

    def handle_name(self, msg, name):
        el = msg.attr('el')
        idx1 = self.index(tk.INSERT)
        self.insert(tk.END, name + '：')
        idx2 = self.index(tk.INSERT)
        for item in el:
            if item['eid'] == '1500000004':
                self.tag_add('red_name', idx1, idx2)
            elif item['eid'] == '1500000082':
                self.tag_add('gold_name', idx1, idx2)
            else:
                self.tag_add('name', idx1, idx2)

    def handle_text(self, msg):
        idx1 = self.index(tk.INSERT)
        self.text_insert(msg.attr('txt'))
        idx2 = self.index(tk.INSERT)
        col = msg.attr('col')
        if col and int(col) > 0:
            self.tag_add(color[col], idx1, idx2)
        else:
            self.tag_add('col', idx1, idx2)

    def text_insert(self, text):
        res = pattern.split(text)
        for idx, item in enumerate(res):
            if idx % 2 == 0 and item:
                self.insert(tk.END, item)
            elif idx % 2 == 1 and item:
                try:
                    image = self.face_img['%s.png' % item]
                    self.image_create(tk.END, image=image)
                except KeyError:
                    self.insert(tk.END, '[emot:dy%s]' % item)
        self.see(tk.END)
        self.insert(tk.END, '\n')

    def cq(self, dlv, dc, tag):
        digit = len(str(dc))
        width = width_cq[digit]

        canvas = tk.Canvas(self, bg='white', borderwidth=0, width=width, height=21, highlightthickness=0)
        if tag:
            canvas.configure(bg='yellow')
        canvas.create_rectangle(11, 2, width+1, 19, fill=color_cq[dlv], width=0)
        canvas.create_image(0, 0, anchor=tk.NW, image=self.static_img['cq_no0%s.png' % dlv])
        canvas.create_text(width/2+10, 10, fill='white', text='x%s' % dc)
        return canvas

    def bandge(self, bl, bnn, tag):
        bl = int(bl)
        canvas = tk.Canvas(self, bg='white', borderwidth=0, width=62, height=24, highlightthickness=0)
        if tag:
            canvas.configure(bg='yellow')
        canvas.create_image(0, 4, anchor=tk.NW, image=self.static_img[bandage[bl]['bg']])
        canvas.create_text(20, 12, fill='white', text=bnn)
        canvas.create_image(40, 0, anchor=tk.NW, image=self.static_img[bandage[bl]['md']])
        canvas.create_image(51, 12, image=self.lv_img['%s.png' % bl])
        return canvas


def copy():
    i, y = 1, 0
    image_raw = Image.open('./static/anchor-level.png')
    while i < 101:
        box = (0, y, 50, y+20)
        image = image_raw.crop(box)
        image.save('./static/LV/anchorLV%s.png' % i)
        i += 1
        y += 23


def download():
    i = 70
    url = 'https://shark.douyucdn.cn/app/douyu/res/page/room-normal/level/LV%s.gif'
    file = './static/LV/LV%s.gif'
    while i < 120:
        res = requests.get(url % i)
        if res.status_code == 200:
            with open(file % i, 'wb') as f:
                f.write(res.content)

        i += 1


def load_image(path, ins):
    files = os.listdir(path)
    for file in files:
        if file.endswith(('.png', '.gif')):
            img = Image.open(path + '/' + file)
            image = ImageTk.PhotoImage(img)
            ins[file] = image


class Tab(tk.Tk):
    face_img = {}
    static_img = {}
    lv_img = {}
    starList = ['小缘']
    message = Message(deserialize(data))

    def __init__(self):
        super(Tab, self).__init__()
        self.window()
        self.load_static()

    def window(self):
        self.notebook = ttk.Notebook()
        frame = tk.Frame()
        font = Font(size=12)
        self.txt = Text(frame, self.static_img, self.lv_img, self.face_img, font=font)
        bar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.txt.yview)
        self.txt.config(yscrollcommand=bar.set)
        bar.pack(fill=tk.Y, side=tk.RIGHT)
        self.txt.pack(fill=tk.BOTH, expand=1)
        self.notebook.add(frame, text='全部')
        self.frame1 = tk.Frame()
        self.notebook.add(self.frame1, text='关注', compound=tk.RIGHT)
        self.text = tk.Text(self.frame1)
        self.text.pack(fill=tk.BOTH, expand=1)
        self.notebook.pack(fill=tk.BOTH, expand=1)
        button = tk.Button(text='更新', command=self.up)
        button.place(relx=0.5)
        self.notebook.bind('<<NotebookTabChanged>>', self.old)

    def up(self):
        self.txt.handle_message(self.message)

    def new(self):
        if self.notebook.select() != str(self.frame1):
            self.notebook.tab(1, image=self.static_img['new.png'])

    def old(self, event):
        if self.notebook.select() == str(self.frame1):
            self.notebook.tab(1, image='')

    def load_static(self):
        load_image('./face', self.face_img)
        load_image('./static', self.static_img)
        load_image('./static/LV', self.lv_img)


if __name__ == '__main__':
    app = Tab()
    app.mainloop()
