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
        self.insert('LV120', 'hiof阿斯加粉丝', '后是哦发件唉哦发窘撒娇地哦撒娇覅噢撒积分iOS叫法')

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
        self.tree_view(frame_danmaku)
        notebook.add(frame_danmaku, text='弹幕')

        frame_star = ttk.Frame()
        # self.star_text(frame_star)
        notebook.add(frame_star, text='关注')

        notebook.place(relheight=1, relwidth=1)

    def tree_view(self, frame):

        columns = ('等级', '昵称', '弹幕')
        xbar = ttk.Scrollbar(frame, orient=tk.HORIZONTAL)
        ybar = ttk.Scrollbar(frame, orient=tk.VERTICAL)

        self.tree = ttk.Treeview(frame, columns=columns, show='headings',
                                 xscrollcommand=xbar.set, yscrollcommand=ybar.set, style='tree.Treeview')
        xbar['command'] = self.tree.xview
        xbar.pack(fill=tk.X, side=tk.BOTTOM)
        ybar['command'] = self.tree.yview
        ybar.pack(fill=tk.Y, side=tk.RIGHT)

        for col in columns:
            self.tree.heading(col, text=col)
        self.tree.column('等级', width=55, stretch=0)
        self.tree.column('昵称', width=180, stretch=0)

        self.tree.pack(fill=tk.BOTH, expand=1)

    # def star_text(self, frame):
    #     # ybar = ttk.Scrollbar(frame, orient=tk.VERTICAL)
    #     text = ROSText(frame)
    #     # ybar['command'] = text.yview
    #     # ybar.pack(fill=tk.Y, side=tk.RIGHT)
    #     text.pack(fill=tk.BOTH, expand=1)

    def window_right(self, frame):
        frame_info = ttk.LabelFrame(frame, text='主播信息：', height=250)
        frame_info.place(relwidth=1)

    def insert(self, lv, name, value):
        col_w = self.tree.column('弹幕', width=None)
        print(self.wrap_text(col_w, value))

    def wrap_text(self, col_w, value):
        length = len(value)
        text_w = self.font.measure(value)
        while col_w < text_w:
            length -= 1
            value = value[0:length]
            text_w = self.font.measure(value)
        else:
            return value

    def frame_resize(self, event, frame):
        frame.configure(width=event.width - 250)


if __name__ == '__main__':
    app = Window()
    app.master.geometry('1000x600+300+150')
    app.master.mainloop()
    # a = 'iofsjiof'
    # if a[0:0] == '':
    #     print(True)
