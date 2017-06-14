import tkinter as tk
from tkinter import ttk
from tkinter.font import Font
from tkinter.scrolledtext import ScrolledText


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


class Window(ttk.Frame):
    def __init__(self, *args, **kwargs):
        super(Window, self).__init__(*args, **kwargs)
        self.s = ttk.Style()
        self.s.configure('tree.Treeview', font=('Microsoft YaHei', 11))
        self.font = Font(family='Microsoft YaHei', size=11)
        self.pack(expand=1, fill=tk.BOTH)
        self.window()

    def window(self):
        frame_left = ttk.Frame()
        frame_left.place(relx=0, rely=0, relheight=1)
        self.window_left(frame_left)

        frame_right = ttk.Frame(width=250)
        frame_right.grid_propagate(0)
        frame_right.place(anchor=tk.NE, relx=1, rely=0, relheight=1)
        self.window_right(frame_right)
        # self.update()
        self.bind('<Configure>', lambda x: self.frame_resize(x, frame_left))

    def window_left(self, frame):
        notebook = ttk.Notebook(frame, padding=(10, 10, 0, 10))

        frame_danmaku = ttk.Frame()
        self.danmaku_tree = self.tree_view(frame_danmaku, ('等级', '昵称', '弹幕'))
        self.danmaku_tree.column('等级', width=55, stretch=0)
        self.danmaku_tree.column('昵称', width=180, stretch=0)

        notebook.add(frame_danmaku, text='弹幕')

        frame_star = ttk.Frame()
        self.star(frame_star)
        notebook.add(frame_star, text='关注')

        notebook.place(relheight=1, relwidth=1)

    def star(self, frame):
        frame_top = ttk.Frame(frame)
        frame_top.place(relwidth=1, relheight=0.6, rely=0)

        text_tree = self.tree_view(frame_top, ('时间', '昵称', '弹幕'))
        text_tree.column('时间', stretch=0, width=160)
        text_tree.column('昵称', stretch=0, width=180)

        frame_bottom = ttk.Frame(frame)
        frame_bottom.place(relwidth=1, relheight=0.4, rely=0.6)

        gift_tree = self.tree_view(frame_bottom, ('昵称', '礼物', '连击'))
        gift_tree.column('昵称', stretch=0, width=180)

    def window_right(self, frame):
        frame_info = ttk.LabelFrame(frame, text='主播信息：', height=250)
        frame_info.place(relwidth=1)

    def tree_view(self, frame, columns):
        xbar = ttk.Scrollbar(frame, orient=tk.HORIZONTAL)
        ybar = ttk.Scrollbar(frame, orient=tk.VERTICAL)

        tree = ttk.Treeview(frame, columns=columns, show='headings',
                            xscrollcommand=xbar.set, yscrollcommand=ybar.set, style='tree.Treeview')
        xbar.config(command=tree.xview)
        xbar.pack(fill=tk.X, side=tk.BOTTOM)
        ybar.config(command=tree.yview)
        ybar.pack(fill=tk.Y, side=tk.RIGHT)

        for col in columns:
            tree.heading(col, text=col)

        tree.pack(fill=tk.BOTH, expand=1)
        return tree

    def insert(self, lv, name, value):
        value = value.replace('\n', '')
        self.danmaku_tree.insert('', tk.END, values=(lv, name, value))
        text_w = self.font.measure(value)
        if self.danmaku_tree.column('弹幕', width=None) < text_w:
            self.danmaku_tree.column('弹幕', width=text_w + 10)

    def frame_resize(self, event, frame):
        frame.configure(width=event.width - 250)


if __name__ == '__main__':
    app = Window()
    app.master.geometry('1000x600+300+150')
    app.master.mainloop()
    # a = 'iofsjiof'
    # if a[0:0] == '':
    #     print(True)
