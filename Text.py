import os
import re
import tkinter as tk
from PIL import ImageTk, Image
from tkinter import ttk

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


class Text(tk.Tk):
    face = {}

    def __init__(self):
        super(Text, self).__init__()
        self.read_face()
        self.frame = tk.Frame()
        self.frame.pack()
        self.txt = ROSText(self.frame, wrap=tk.WORD)
        self.txt.pack()
        self.txt.tag_config('anchor', background='yellow')

    def text_insert(self, text, tag=None):
        index1 = self.txt.index(tk.INSERT)
        res = pattern.split(text)
        for idx, item in enumerate(res):
            if idx % 2 == 0 and item:
                self.txt.insert(tk.END, item)
            elif idx % 2 == 1:
                try:
                    image = self.face['%s.png' % item]
                    self.txt.image_create(tk.END, image=image, align=tk.BASELINE)
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

    def tag(self):
        self.txt.tag_config('')


if __name__ == '__main__':
    root = Text()
    # root.minsize(height=500, width=800)
    root.mainloop()
