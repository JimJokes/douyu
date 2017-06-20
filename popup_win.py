import webbrowser
import tkinter as tk
from tkinter import ttk
from tkinter.font import Font
from PIL import Image, ImageTk


# 弹窗
class Popup(tk.Toplevel):
    alpha = 0
    width = 400
    height = 90
    x_src = 20
    y_src = 50
    y_des = 50
    images = []

    def __init__(self, master=None, **kwargs):
        super(Popup, self).__init__(master=master, **kwargs)
        self.style()
        self.attribute()
        self.move_id = None
        self.overrideredirect(True)

    def popup(self):
        self.fade_in()
        self.after(5000, self.fade_out)

    def move_up(self, distance=90):
        self.y_des = self.y_des + distance + 10
        if self.move_id:
            self.after_cancel(self.move_id)
        self.move_y_up(self.width, self.height, self.x_src)

    def move_down(self, distance=90):
        self.y_des = self.y_des - distance - 10
        if self.move_id:
            self.after_cancel(self.move_id)
        self.move_y_down(self.width, self.height, self.x_src)

    def move_y_up(self, width, height, x):
        if self.y_src < self.y_des:
            self.y_src += 10
            self.position(width, height, x, self.y_src)
            self.move_id = self.after(10, self.move_y_up, width, height, x)
        else:
            self.position(width, height, x, self.y_des)
            self.y_src = self.y_des
            self.move_id = None

    def move_y_down(self, width, height, x):
        if self.y_src > self.y_des:
            self.y_src -= 10
            self.position(width, height, x, self.y_src)
            self.move_id = self.after(10, self.move_y_down, width, height, x)
        else:
            self.position(width, height, x, self.y_des)
            self.y_src = self.y_des
            self.move_id = None

    def position(self, width, height, x, y):
        self.geometry('%sx%s-%s-%s' % (width, height, x, y))

    def attribute(self):
        self.resizable(False, False)
        self.attributes('-topmost', 1)
        self.overrideredirect(True)
        self.attributes('-alpha', self.alpha)

    def style(self):
        s = ttk.Style()
        s.configure('TFrame', background='white')
        s.configure('TLabel', background='white', font=('Microsoft YaHei', 9))
        s.configure('title.TLabel', font=('Microsoft YaHei', 11))

    def fade_in(self):
        if self.alpha < 1:
            self.alpha += 0.1
            self.attributes('-alpha', self.alpha)
            self.after(30, self.fade_in)
        else:
            self.alpha = 1
            self.attributes('-alpha', self.alpha)

    def fade_out(self):
        if self.alpha > 0:
            self.alpha -= 0.1
            self.attributes('-alpha', self.alpha)
            self.id = self.after(30, self.fade_out)
        else:
            self.alpha = 0
            self.attributes('-alpha', self.alpha)
            self.id = None


# 开播提醒弹窗
class LivePopup(Popup):
    def __init__(self, master=None, **kwargs):
        super(LivePopup, self).__init__(master=master, **kwargs)
        self.position(self.width, self.height, self.x_src, self.y_src)
        self.window()

    def window(self):
        frame = ttk.Frame(self, padding=(2, 10, 2, 10), cursor='hand2', relief=tk.RAISED)
        frame.pack(fill=tk.BOTH, expand=1)

        frame_image = ttk.Frame(frame)
        frame_image.place(relheight=1, relwidth=0.3)
        self.window_image(frame_image)

        frame_info = ttk.Frame(frame)
        frame_info.place(relheight=1, relwidth=0.65, relx=0.32)
        self.window_info(frame_info)

        # close_button = ttk.Label(self, text='x', anchor=tk.CENTER, width=2)
        # close_button.place(anchor=tk.NE, relx=1)

        self.bind_event((frame, frame_info, frame_image))

    def window_image(self, frame):
        img = Image.open('icon.ico')
        img = ImageTk.PhotoImage(img)
        self.images.append(img)
        image = ttk.Label(frame, image=img)
        image.place(relheight=1, relwidth=1)

        self.bind_event((image, ))

    def window_info(self, frame):
        title = ttk.Label(frame, anchor=tk.W, style='title.TLabel', text='hi的哦啊发及哦啊鸡动发窘', wraplength=240)
        title.place(relwidth=1, relheight=0.5)

        status = ttk.Label(frame, anchor=tk.W, text='直播中（已播120分钟）')
        status.place(relwidth=1, relheight=0.25, rely=0.5)

        owner = ttk.Label(frame, anchor=tk.W, text='小缘', foreground='gray')
        owner.place(relwidth=1, relheight=0.25, rely=0.75)

        self.bind_event((title, status, owner))

    def bind_event(self, frames):
        for frame in frames:
            frame.bind('<Button-1>', self.open_browser)

    def open_browser(self, *args):
        webbrowser.open('www.baidu.com')


# 关注信息弹窗
class StarPopup(Popup):
    def __init__(self, master=None, **kwargs):
        super(StarPopup, self).__init__(master=master, **kwargs)
        self.height = 60
        self.font = Font(family='Microsoft YaHei', size=11)
        self.position(self.width, self.height, self.x_src, self.y_src)
        self.window()

    def window(self):
        frame = ttk.Frame(self, padding=(5, 2, 5, 2), relief=tk.RAISED)
        frame.pack(fill=tk.BOTH, expand=1)

        # title = ttk.Label(frame, text='[15256815]关注', style='title.TLabel', wraplength=70)
        # title.place(relwidth=0.2, relheight=1)

        name = ttk.Label(frame, text='小缘的异次元大包子：', style='title.TLabel')
        name.place(relwidth=0.4, relheight=1)

        text = ttk.Label(frame, text='asdfghjklqwertyuiopzxcvbnm123456789', style='title.TLabel', wraplength=230)
        text.place(relwidth=0.6, relheight=1, relx=0.4)
