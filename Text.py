import re
import tkinter as tk
from tkinter import ttk
from tkinter.font import Font

from utils import lv, color, noble, color_cq, width_cq, bandage

pattern = re.compile(r'\[emot:dy([0-9]+)]')


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


class BarrageText(ROSText):
    def __init__(self, master, static_img, lv_img,
                 face_img, *args, **kwargs):
        font = Font(size=11)
        super(BarrageText, self).__init__(master, spacing1=5, insertwidth=0, font=font, *args, **kwargs)
        bar = ttk.Scrollbar(master, orient=tk.VERTICAL, command=self.yview)
        self.config(yscrollcommand=bar.set)
        bar.pack(fill=tk.Y, side=tk.RIGHT)
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

    def handle_message(self, message, star=False):
        images = []
        name = 'name'
        el = message.el
        if el:
            for item in el:
                if item['eid'] == '1500000005':
                    images.append(self.static_img['madel-s1.png'])
                elif item['eid'] == '1500000003':
                    images.append(self.static_img['madel-s2.png'])
                elif item['eid'] == '1500000002':
                    images.append(self.static_img['madel-s3.png'])
                elif item['eid'] == '1500000160':
                    images.append(self.static_img['firstpay-award-icon.png'])
                elif item['eid'] == '1500000004':
                    name = 'red_name'
                elif item['eid'] == '1500000082':
                    name = 'gold_name'

        self.handle_role(message)
        self.handle_noble(message)
        self.handle_cq(message, star)
        self.handle_madel(images)
        self.handle_bandge(message, star)
        self.handle_level(message)
        self.handle_name(message, name)
        self.handle_text(message)

    def handle_uenter(self, message):
        self.handle_noble(message)
        self.handle_cq(message)
        self.handle_level(message)
        self.handle_name(message, 'name', enter=True)
        self.insert(tk.END, '进入直播间！')

    def handle_role(self, msg):
        role = None
        if msg.pg in ('5', '2') and msg.sahf == '1':
            role = 'super_admin'
        elif msg.rg == '4':
            role = 'roomadmin'
        elif msg.rg == '5':
            role = 'anchor'
        if role:
            try:
                self.image_create(tk.END, image=self.static_img['%s.png' % role])
            except KeyError:
                pass
            self.insert(tk.END, ' ')

    def handle_noble(self, msg):
        nl = msg.nl
        if nl:
            try:
                self.image_create(tk.END, image=self.static_img[noble[nl]])
            except KeyError:
                pass
            self.insert(tk.END, ' ')

    def handle_cq(self, msg, star=False):
        dlv = msg.dlv
        dc = msg.dc
        bdlv = msg.bdlv
        if dlv and dc and int(dlv) > 0 and int(dc) > 0:
            self.window_create(tk.END, window=self.cq(dlv, dc, star))
            self.insert(tk.END, ' ')
        elif bdlv and int(bdlv) > 0:
            try:
                self.image_create(tk.END, image=self.static_img['cq_other.png'])
            except KeyError:
                pass
            self.insert(tk.END, ' ')

    def handle_madel(self, images):
        for image in images:
            self.image_create(tk.END, image=image)
            self.insert(tk.END, ' ')

    def handle_bandge(self, msg, star=False):
        bnn = msg.bnn
        bl = msg.bl
        if bnn and bl:
            self.window_create(tk.END, window=self.bandge(bl, bnn, star))
            self.insert(tk.END, ' ')

    def handle_level(self, msg):
        ol = msg.ol
        level = msg.level
        try:
            if ol and int(ol) > 0:
                self.image_create(tk.END, image=self.lv_img['anchorLV%s.png' % ol])
                self.insert(tk.END, ' ')
            elif level and int(level) > 0:
                self.image_create(tk.END, image=self.lv_img[lv[int(level)]])
                self.insert(tk.END, ' ')
        except KeyError:
            pass

    def handle_name(self, msg, name, enter=False):
        self.insert(tk.END, msg.nn, (name,))
        if not enter:
            self.insert(tk.END, '：', (name,))

    def handle_text(self, msg):
        col = msg.col
        if col and 7 > int(col) > 0:
            tag = color[col]
        else:
            tag = 'col'
        self.text_insert(msg.txt, tag)

    def text_insert(self, text, tag):
        res = pattern.split(text)
        for idx, item in enumerate(res):
            if idx % 2 == 0 and item:
                self.insert(tk.END, item, (tag, ))
            elif idx % 2 == 1 and item:
                try:
                    image = self.face_img['%s.png' % item]
                    self.image_create(tk.END, image=image)
                except KeyError:
                    self.insert(tk.END, '[emot:dy%s]' % item, (tag, ))

    def cq(self, dlv, dc, star=False):
        digit = len(str(dc))
        width = width_cq[digit]

        canvas = tk.Canvas(self, bg='white', borderwidth=0, width=width, height=21, highlightthickness=0)
        if star:
            canvas.configure(bg='yellow')
        canvas.create_rectangle(11, 2, width+1, 19, fill=color_cq[dlv], width=0)
        try:
            canvas.create_image(0, 0, anchor=tk.NW, image=self.static_img['cq_no0%s.png' % dlv])
        except KeyError:
            pass
        canvas.create_text(width/2+10, 10, fill='white', text='x%s' % dc)
        return canvas

    def bandge(self, bl, bnn, star=False):
        bl = int(bl)
        canvas = tk.Canvas(self, bg='white', borderwidth=0, width=62, height=24, highlightthickness=0)
        if star:
            canvas.configure(bg='yellow')
        try:
            canvas.create_image(0, 4, anchor=tk.NW, image=self.static_img[bandage[bl]['bg']])
            canvas.create_text(20, 12, fill='white', text=bnn)
            canvas.create_image(40, 0, anchor=tk.NW, image=self.static_img[bandage[bl]['md']])
            canvas.create_image(51, 12, image=self.lv_img['%s.png' % bl])
        except KeyError:
            pass
        return canvas
