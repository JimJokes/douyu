import os
import sys
import tkinter as tk
from tkinter import ttk
from tkinter.font import Font
from tkinter.messagebox import showwarning

import time
from PIL import Image, ImageTk

import utils

star_file = os.path.join(os.getcwd(), 'starList.txt')

if getattr(sys, 'frozen', False):
    icon = os.path.join(getattr(sys, '_MEIPASS', '.'), 'icon.ico')
else:
    icon = os.path.join(os.path.dirname(__file__), 'icon.ico')


def frame_resize(event, frame, size, direction):
    if direction == tk.X:
        frame.config(width=event.width - size)
    elif direction == tk.Y:
        frame.config(height=event.height - size)


class Window(tk.Tk):
    def __init__(self, *args, **kwargs):
        super(Window, self).__init__(*args, **kwargs)
        self.lock_text = tk.StringVar()
        self.s = ttk.Style()
        self.s.configure('tree.Treeview', font=('Microsoft YaHei', 11))
        self.font = Font(family='Microsoft YaHei', size=11)
        self.frame = ttk.Frame()
        self.frame.pack(expand=1, fill=tk.BOTH)
        self.window()
        self.read_stars()

    def window(self):
        frame_left = ttk.Frame(self.frame)
        frame_left.place(relx=0, rely=0, relheight=1)
        self.window_left(frame_left)

        frame_right = ttk.Frame(self.frame, width=250)
        frame_right.grid_propagate(0)
        frame_right.place(anchor=tk.NE, relx=1, rely=0, relheight=1)
        self.window_right(frame_right)
        # self.update()
        self.frame.bind('<Configure>', lambda x: frame_resize(x, frame_left, 250, tk.X))

    def window_left(self, frame):
        notebook = ttk.Notebook(frame, padding=(10, 10, 10, 10))

        frame_danmaku = ttk.Frame()
        danmaku_tree = self.tree_view(frame_danmaku, ('昵称', '弹幕'), x=1, y=1, style='tree.Treeview')
        # danmaku_tree.column('等级', width=55, stretch=0)
        danmaku_tree.column('昵称', width=180, stretch=0)

        notebook.add(frame_danmaku, text='弹幕')

        frame_star = ttk.Frame()
        self.window_star(frame_star)
        notebook.add(frame_star, text='关注')

        notebook.place(relheight=1, relwidth=1)

        lock_button = ttk.Button(frame, textvariable=self.lock_text, width=5, command=self.lock)
        self.lock_text.set('锁屏')
        lock_button.place(anchor=tk.NE, y=10, relx=0.9)

    def window_star(self, frame):
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
        frame_mid.place(relwidth=1, height=80, y=220)
        self.window_id(frame_mid)

        frame_bottom = ttk.Frame(frame)
        frame_bottom.place(relwidth=1, y=300)
        self.window_star_list(frame_bottom)

        frame.bind('<Configure>', lambda x: frame_resize(x, frame_bottom, 300, tk.Y))

    def window_info(self, frame):
        info_notebook = ttk.Notebook(frame, padding=(0, 10, 10, 0))

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

    def window_id(self, frame):
        label = ttk.Label(frame, text='直播间ID：')
        label.place(anchor=tk.NE, relx=0.5, rely=0.1, height=20, relwidth=0.4)

        self.entry_id = ttk.Entry(frame)
        self.entry_id.place(relx=0.5, rely=0.1, height=20, relwidth=0.4)

        self.start_button = ttk.Button(frame, text='连接', command=self.on)
        self.start_button.place(anchor=tk.NE, relx=0.4, rely=0.5, width=60)
        self.stop_button = ttk.Button(frame, text='断开连接', state=tk.DISABLED, command=self.off)
        self.stop_button.place(relx=0.6, rely=0.5, width=60)

    def window_star_list(self, frame):
        star_notebook = ttk.Notebook(frame, padding=(0, 0, 10, 10))

        frame_star = ttk.Frame()
        self.stars = tk.Text(frame_star)
        vbar = ttk.Scrollbar(frame_star, command=self.stars.yview)
        vbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.stars.config(yscrollcommand=vbar.set)
        self.stars.pack(fill=tk.BOTH, expand=1)

        star_notebook.add(frame_star, text='关注列表')
        star_notebook.place(relwidth=1, relheight=1)

        save_button = ttk.Button(frame, text='保存', width=5, command=self.save_stars)
        save_button.place(anchor=tk.NE, relx=0.6, rely=0)
        reload_button = ttk.Button(frame, text='更新', width=5)
        reload_button.place(anchor=tk.NE, relx=0.8, rely=0)

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

    def on(self):
        room_id = self.entry_id.get()
        if not room_id.isdigit():
            showwarning('直播间ID不正确', '请输入正确的直播间ID！')
        else:
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.ACTIVE)

    def off(self):
        self.start_button.config(state=tk.ACTIVE)
        self.stop_button.config(state=tk.DISABLED)

    def lock(self):
        if utils.CheckVar:
            utils.CheckVar = False
            self.lock_text.set('滚屏')
        else:
            utils.CheckVar = True
            self.lock_text.set('锁屏')

    def read_stars(self):
        self.stars.delete(1.0, tk.END)
        if not os.path.exists(star_file):
            with open(star_file, 'w', encoding='utf-8'):
                pass
        else:
            with open(star_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                for line in lines:
                    utils.stars.append(line.strip())
                    self.stars.insert(tk.END, line)

    def save_stars(self):
        text = self.stars.get(1.0, tk.END)
        with open(star_file, 'w', encoding='utf-8') as f:
            for star in text.split('\n'):
                if star.strip():
                    f.write(star.strip()+'\n')
        self.read_stars()


# 弹窗
class Popup(tk.Toplevel):
    alpha = 0
    src = 50
    des = 50
    images = []

    def __init__(self, master=None, **kwargs):
        super(Popup, self).__init__(master=master, **kwargs)
        self.style()
        self.attribute()
        self.move_id = None
        self.overrideredirect(True)

    def popup(self):
        self.fade_in()
        self.after(8000, self.fade_out)

    def move_up(self):
        self.des = self.des + 100
        if self.move_id:
            self.after_cancel(self.move_id)
        self.move()

    def move(self):
        if self.src < self.des:
            self.src += 10
            self.geometry('%sx%s-%s-%s' % (400, 90, 20, self.src))
            self.move_id = self.after(10, self.move)
        else:
            self.geometry('%sx%s-%s-%s' % (400, 90, 20, self.des))
            self.src = self.des
            self.move_id = None

    def attribute(self):
        self.resizable(False, False)
        self.attributes('-topmost', 1)
        self.overrideredirect(True)
        # self.attributes('-alpha', 0)

    def style(self):
        s = ttk.Style()
        s.configure('TFrame', background='white')
        s.configure('TLabel', background='white', font=('Microsoft YaHei', 10))
        s.configure('title.TLabel', font=('Microsoft YaHei', 11))

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
            self.alpha = 0


# 开播提醒弹窗
class LivePopup(Popup):
    def __init__(self, master, **kwargs):
        super(LivePopup, self).__init__(master=master, **kwargs)
        self.geometry('%sx%s-%s-%s' % (400, 90, 20, self.src))
        self.window()

    def window(self):
        frame = ttk.Frame(self, padding=(0, 5, 0, 5))
        frame.pack(fill=tk.BOTH, expand=1)

        frame_image = ttk.Frame(frame)
        frame_image.place(relheight=1, relwidth=0.3)
        self.window_image(frame_image)

        frame_info = ttk.Frame(frame)
        frame_info.place(relheight=1, relwidth=0.65, relx=0.32)
        self.window_info(frame_info)

        close = ttk.Label(self, text='x', anchor=tk.CENTER, width=2)
        close.place(anchor=tk.NE, relx=1,)

    def window_image(self, frame):
        img = Image.open('icon.ico')
        img = ImageTk.PhotoImage(img)
        self.images.append(img)
        image = ttk.Label(frame, image=img)
        image.place(relheight=1, relwidth=1)

    def window_info(self, frame):
        title = ttk.Label(frame, anchor=tk.W, style='title.TLabel', text='hi的哦啊发及哦啊鸡动发窘', wraplength=240)
        title.place(relwidth=1, relheight=0.5)

        status = ttk.Label(frame, anchor=tk.W, text='直播中（已播120分钟）')
        status.place(relwidth=1, relheight=0.25, rely=0.5)

        owner = ttk.Label(frame, anchor=tk.W, text='小缘', foreground='gray')
        owner.place(relwidth=1, relheight=0.25, rely=0.75)


# 关注信息弹窗
class StarPopup(Popup):
    def __init__(self, master, **kwargs):
        super(StarPopup, self).__init__(master=master, **kwargs)
        self.geometry('%sx%s-%s-%s' % (400, 90, 20, self.src))
        self.window()

    def window(self):
        frame = ttk.Frame(self, padding=(0, 10, 0, 10))
        frame.pack(fill=tk.BOTH, expand=1)

    def move_up(self):
        self.des = self.des + 100
        if self.move_id:
            self.after_cancel(self.move_id)
        self.move()


if __name__ == '__main__':
    # app = Window()
    # app.geometry('1000x600+300+150')
    # app.mainloop()
    # app = Popup()
    # app.mainloop()
    # top = tk.Tk()
    # s = ttk.Style()
    # print(s.layout('TLabel'))
    # print(s.element_options('TLabel.padding'))
    # print(s.lookup('TLabel.label', 'padding'))
    # top.destroy()
    # top.mainloop()
    top = tk.Tk()
    app = StarPopup(top)
    app.move_up()
    top.mainloop()
