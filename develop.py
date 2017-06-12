import tkinter as tk
from tkinter import ttk
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
        self.bind('<Configure>', lambda x: frame_resize(x, frame_left))

    def window_left(self, frame):
        notebook = ttk.Notebook(frame, padding=(10, 10, 0, 10))

        frame_danmaku = ttk.Frame()
        tree = ttk.Treeview(frame_danmaku, columns=('等级', '昵称', '弹幕'), show='headings')
        tree.heading('等级', text='等级')
        tree.heading('昵称', text='昵称')
        tree.heading('弹幕', text='弹幕')
        print(tree.column('弹幕'))
        tree.insert('', tk.END, values=('LV30', '缘总包养的小三', '好大方活啊加大到家啊覅哦hi哦\n啊是的发送机啊hi哦啊三角阀阿海'))
        tree.place(relheight=1, relwidth=1)
        notebook.add(frame_danmaku, text='弹幕')

        frame_star = ttk.Frame()
        notebook.add(frame_star, text='关注')

        notebook.place(relheight=1, relwidth=1)

    def window_right(self, frame):
        frame_info = ttk.LabelFrame(frame, text='主播信息：', height=250)
        frame_info.place(relwidth=1)


def frame_resize(event, frame):
    frame.configure(width=event.width-250)


if __name__ == '__main__':
    app = Window()
    app.master.geometry('1000x600+300+150')
    app.master.mainloop()
    # s = ttk.Style()
    # b = ttk.Treeview()
    # print(b.winfo_class())
    # print(s.element_options('Treeview.label'))
    # print(s.lookup('Treeview.label', 'background'))
