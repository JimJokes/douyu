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
        self.bind('<Configure>', lambda x: self.frame_resize(x, frame_left, 250, tk.X))

    def window_left(self, frame):
        notebook = ttk.Notebook(frame, padding=(10, 10, 0, 10))

        frame_danmaku = ttk.Frame()
        danmaku_tree = self.tree_view(frame_danmaku, ('等级', '昵称', '弹幕'), x=1, y=1, style='tree.Treeview')
        danmaku_tree.column('等级', width=55, stretch=0)
        danmaku_tree.column('昵称', width=180, stretch=0)

        notebook.add(frame_danmaku, text='弹幕')

        frame_star = ttk.Frame()
        self.star(frame_star)
        notebook.add(frame_star, text='关注')

        notebook.place(relheight=1, relwidth=1)

    def star(self, frame):
        frame_top = ttk.Frame(frame)
        frame_top.place(relwidth=1, relheight=0.6, rely=0)

        text_tree = self.tree_view(frame_top, ('时间', '昵称', '弹幕'), x=1, y=1, style='tree.Treeview')
        text_tree.column('时间', stretch=0, width=160)
        text_tree.column('昵称', stretch=0, width=180)

        frame_bottom = ttk.Frame(frame)
        frame_bottom.place(relwidth=1, relheight=0.4, rely=0.6)

        gift_tree = self.tree_view(frame_bottom, ('时间', '昵称', '礼物', '连击'), y=1, style='tree.Treeview')
        gift_tree.column('时间', stretch=0, width=160)
        gift_tree.column('昵称', stretch=0, width=180)
        gift_tree.column('连击', stretch=0, width=50)

    def window_right(self, frame):
        frame_top = ttk.Frame(frame)
        frame_top.place(relwidth=1, height=220, rely=0)
        self.window_info(frame_top)

        frame_mid = ttk.Frame(frame)
        frame_mid.place(relwidth=1, height=100, y=250)

        frame_bottom = ttk.Frame(frame)
        frame_bottom.place(relwidth=1, y=500)

        frame.bind('<Configure>', lambda x: self.frame_resize(x, frame_bottom, 350, tk.Y))

    def window_info(self, frame):
        info_notebook = ttk.Notebook(frame, padding=(0, 10, 10, 0))
        # frame_info = ttk.Frame()
        info_tree = ttk.Treeview(columns=('1', '2'), show='tree')
        info_tree.column('#0', width=0, stretch=0)
        info_tree.column('1', stretch=0, width=80)
        info_tree.column('2', stretch=0, width=154)
        info_notebook.add(info_tree, text='主播信息：')
        info_notebook.place(relwidth=1, relheight=1)
        info_tree.insert('', tk.END, values=('直播间标题：',))
        info_tree.insert('', tk.END)
        info_tree.insert('', tk.END, values=('主播：',))
        info_tree.insert('', tk.END, values=('关注：',))
        info_tree.insert('', tk.END, values=('体重：',))
        info_tree.insert('', tk.END, values=('开播状态：',))
        info_tree.insert('', tk.END, values=('人气：',))
        info_tree.insert('', tk.END, values=('上次直播：',))
        info_tree.insert('', tk.END, values=('更新时间：',))

    def tree_view(self, frame, columns, x=None, y=None, style='Treeview'):
        tree = ttk.Treeview(frame, columns=columns, show='headings', style=style)
        tree.columns = columns
        if x:
            xbar = ttk.Scrollbar(frame, orient=tk.HORIZONTAL, command=tree.xview)
            tree.config(xscrollcommand=xbar.set)
            xbar.pack(fill=tk.X, side=tk.BOTTOM)
        if y:
            ybar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
            tree.config(yscrollcommand=ybar.set)
            ybar.pack(fill=tk.Y, side=tk.RIGHT)

        for col in columns:
            tree.heading(col, text=col)

        tree.pack(fill=tk.BOTH, expand=1)
        return tree

    def insert(self, tree, values):
        for idx, value in enumerate(values):
            value = value.replace('\n', '')
            text_w = self.font.measure(value)
            if tree.column(tree.columns[idx], width=None) < text_w:
                tree.column(tree.columns[idx], width=text_w + 10)
        tree.insert('', tk.END, values=values)

    def frame_resize(self, event, frame, size, direction):
        if direction == tk.X:
            frame.config(width=event.width - size)
        elif direction == tk.Y:
            frame.config(height=event.height - size)


if __name__ == '__main__':
    app = Window()
    app.master.geometry('1000x600+300+150')
    app.master.mainloop()
    # root = tk.Tk()
    # s = ttk.Style()
    # s.configure('Treeview', font=('Microsoft YaHei', 20), background='red')
    # tree = ttk.Treeview(columns=('1', '2'), show='tree')
    # tree.heading('1', text='123')
    # tree.column('#0', width=0)
    # print(s.element_options('Treeview.padding'))
    # print(s.lookup('Treeview.padding', 'padding'))
    # tree.pack()
    # tree.insert('', tk.END, values=('123', '123'))
    # root.mainloop()
