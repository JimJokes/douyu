import os
import re
import tkinter as tk
from tkinter.font import Font

from PIL import ImageTk, Image

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


class Text(tk.Tk):
    face = {}
    static = {}

    def __init__(self):
        super(Text, self).__init__()
        self.font = Font(size=11)
        self.read_face()
        self.read_static()
        self.frame = tk.Frame()
        self.frame.pack()
        self.txt = ROSText(self.frame, font=self.font)
        self.txt.pack()
        self.txt.tag_config('anchor', background='yellow')
        # self.text_insert('iajfdiojafi')
        self.text_insert('哈哈哈哈[emot:dy010]')
        self.text_insert('哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈hhhhhhhhhhhhhhhhhhhh', tag=1)

    def text_insert(self, text, tag=None):
        index1 = self.txt.index(tk.INSERT)
        self.img_insert(tag)
        res = pattern.split(text)
        for idx, item in enumerate(res):
            if idx % 2 == 0 and item:
                self.txt.insert(tk.END, item)
            elif idx % 2 == 1:
                try:
                    image = self.face['%s.png' % item]
                    self.txt.image_create(tk.END, image=image)
                except KeyError:
                    self.txt.insert(tk.END, '[emot:dy%s]' % item)
        self.txt.see(tk.END)
        self.txt.insert(tk.END, '\n')
        index2 = self.txt.index(tk.INSERT)
        if tag:
            self.txt.tag_add('anchor', index1, index2)

    def read_face(self):
        files = os.listdir('./face')
        for file in files:
            img = Image.open('./face/'+file)
            image = ImageTk.PhotoImage(img)
            self.face[file] = image

    def read_static(self):
        files = os.listdir('./static')
        for file in files:
            img = Image.open('./static/'+file)
            image = ImageTk.PhotoImage(img)
            self.static[file] = image

    def img_insert(self, tag=None):
        self.txt.image_create(tk.END, image=self.static['cq_other.png'])
        self.txt.insert(tk.END, ' ')
        self.txt.image_create(tk.END, image=self.static['madel-s3.png'])
        self.txt.insert(tk.END, ' ')
        self.txt.window_create(tk.END, window=self.pai(tag))
        self.txt.insert(tk.END, ' ')
        self.txt.image_create(tk.END, image=self.static['LV120.gif'])
        self.txt.insert(tk.END, ' ')
        self.txt.insert(tk.END, '缘总包养的小三儿：')

    def pai(self, tag=None):
        canvas = tk.Canvas(self.txt, bg='white', borderwidth=0, width=62, height=24, highlightthickness=0)
        if tag:
            canvas.configure(bg='yellow')
        canvas.create_image(0, 4, anchor=tk.NW, image=self.static['bandgebg_03.png'])
        canvas.create_text(20, 12, fill='white', text='小肚皮')
        canvas.create_image(40, 0, anchor=tk.NW, image=self.static['bandge_03.png'])
        # canvas.create_text(53, 13, fill='white', text='13', font=Font(size=10, weight='bold'))
        canvas.create_image(51, 12, image=self.static['1.png'])
        # canvas.place(width=6, height=2)
        return canvas


if __name__ == '__main__':
    root = Text()
    root.minsize(height=500, width=800)
    root.mainloop()
    # a = b'type@=chatmsg/rid@=74751/ct@=1/uid@=22331021/nn@=132456789kl/txt@=\xe5\xb0\x8f\xe6\xa1\x80\xe5\x8a\xa0\xe6\xb2\xb9\xed\xa0\xbd\xed\xb8\x8a/cid@=ac9917f5308d4831424a010000000000/ic@=avatar@Sdefault@S12/level@=16/sahf@=0/bnn@=/bl@=0/brid@=0/hc@=/el@=eid@AA=1500000113@ASetp@AA=1@ASsc@AA=1@ASef@AA=0@AS@S/\x00'
    # print(a.decode(errors='replace'))
