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
    # images = []

    def __init__(self, master=None, **kwargs):
        super(Popup, self).__init__(master=master, **kwargs)
        self.style()
        self.attribute()
        self.move_id = None
        self.overrideredirect(True)

    # 窗口上移
    def move_up(self, distance=90):
        distance = distance+5
        interval = int(100/distance)
        self.y_des = self.y_des+distance
        if self.move_id:
            self.after_cancel(self.move_id)
        self.move_y_up(self.width, self.height, self.x_src, interval)

    # 窗口下移
    def move_down(self, distance=90):
        distance = distance+5
        interval = int(100/distance)
        self.y_des = self.y_des-distance
        if self.move_id:
            self.after_cancel(self.move_id)
        self.move_y_down(self.width, self.height, self.x_src, interval)

    # 窗口下移事件
    def move_y_up(self, width, height, x, interval):
        if self.y_src < self.y_des:
            self.y_src += 1
            self.position(width, height, x, self.y_src)
            self.move_id = self.after(interval, self.move_y_up, width, height, x, interval)
        else:
            self.position(width, height, x, self.y_des)
            self.y_src = self.y_des
            self.move_id = None

    # 窗口上移事件
    def move_y_down(self, width, height, x, interval):
        if self.y_src > self.y_des:
            self.y_src -= 1
            self.position(width, height, x, self.y_src)
            self.move_id = self.after(interval, self.move_y_down, width, height, x, interval)
        else:
            self.position(width, height, x, self.y_des)
            self.y_src = self.y_des
            self.move_id = None

    # 窗口定位
    def position(self, width, height, x, y):
        self.geometry('%sx%s-%s-%s' % (width, height, x, y))

    # 窗口状态
    def attribute(self):
        self.resizable(False, False)
        self.attributes('-topmost', 1)
        self.overrideredirect(True)
        self.attributes('-alpha', self.alpha)

    # 窗口风格定义
    def style(self):
        s = ttk.Style()
        s.configure('white.TFrame', background='white')
        s.configure('white.TLabel', background='white', font=('Microsoft YaHei', 9))
        s.configure('title.white.TLabel', font=('Microsoft YaHei', 11), foreground='blue')

    def pop_up(self):
        self.fade_in()

    # 窗口淡入
    def fade_in(self):
        if self.alpha < 1:
            self.alpha += 0.1
            self.attributes('-alpha', self.alpha)
            self.after(20, self.fade_in)
        else:
            self.alpha = 1
            self.attributes('-alpha', self.alpha)

    def pop_down(self):
        self.fade_out()

    # 窗口淡出
    def fade_out(self):
        if self.alpha > 0:
            self.alpha -= 0.1
            self.attributes('-alpha', self.alpha)
            self.after(20, self.fade_out)
        else:
            # self.alpha = 0
            # self.attributes('-alpha', self.alpha)
            self.destroy()


# 开播提醒弹窗
class LivePopup(Popup):
    def __init__(self, room, image, title, status, name, master=None, **kwargs):
        super(LivePopup, self).__init__(master=master, **kwargs)
        self.img = None
        self.room = room
        self.image = image
        self.title = title.strip()
        self.status = status.strip()
        self.name = name.strip()
        self.window()
        self.position(self.width, self.height, self.x_src, self.y_src)

    # 基础窗口
    def window(self):
        frame = tk.Frame(self, cursor='hand2', relief=tk.RAISED, bd=2, bg='white')
        frame.pack(fill=tk.BOTH, expand=1)

        frame_image = ttk.Frame(frame, style='white.TFrame')
        frame_image.place(relheight=1, relwidth=0.3)
        self.window_image(frame_image)

        frame_info = ttk.Frame(frame, style='white.TFrame', padding=(0, 0, 0, 5))
        frame_info.place(relheight=1, relwidth=0.68, relx=0.32)
        self.window_info(frame_info)

        # close_button = ttk.Label(self, text='x', anchor=tk.CENTER, width=2)
        # close_button.place(anchor=tk.NE, relx=1)

        self.bind_event((frame, frame_info, frame_image))

    # 图片窗口
    def window_image(self, frame):
        self.lebel_image = ttk.Label(frame, style='white.TLabel', anchor=tk.CENTER)
        self.lebel_image.place(relheight=1, relwidth=1)

        self.bind_event((self.lebel_image, ))

    # 信息窗口
    def window_info(self, frame):
        title = ttk.Label(frame, anchor=tk.W, style='title.white.TLabel', text=self.title, wraplength=265)
        title.place(relwidth=1, relheight=0.5)

        status = ttk.Label(frame, anchor=tk.W, text=self.status, style='white.TLabel')
        status.place(relwidth=1, relheight=0.25, rely=0.5)

        owner = ttk.Label(frame, anchor=tk.W, text=self.name, foreground='gray', style='white.TLabel')
        owner.place(relwidth=1, relheight=0.25, rely=0.75)

        self.bind_event((title, status, owner))

    # 添加图片
    def add_image(self):
        img = Image.open(self.image)
        width = img.width
        height = img.height
        f = min(115 / width, 85 / height)
        width = int(width * f)
        height = int(height * f)
        img = img.resize((width, height), Image.ANTIALIAS)
        self.img = ImageTk.PhotoImage(img)
        self.lebel_image.config(image=self.img)

    # 淡入前插入图片
    def pop_up(self):
        self.add_image()
        self.fade_in()

    # 点击事件绑定
    def bind_event(self, frames):
        for frame in frames:
            frame.bind('<Button-1>', self.open_browser)

    # 打开浏览器事件
    def open_browser(self, event):
        webbrowser.open('www.douyu.com/%s' % self.room)


# 关注信息弹窗
class StarPopup(Popup):
    def __init__(self, name, text, hit=None, master=None, **kwargs):
        super(StarPopup, self).__init__(master=master, **kwargs)
        self.hit_str = tk.StringVar()
        self.font = Font(family='Microsoft YaHei', size=11)
        self.font_bold = Font(family='Microsoft YaHei', size=11, weight='bold')
        self.name = name.strip()
        self.text = text.strip()
        self.hit = hit
        self.height = 30
        self.window()
        self.position(self.width, self.height, self.x_src, self.y_src)

    # 基础窗口
    def window(self):
        # frame = ttk.Frame(self, padding=(5, 0, 5, 0), relief=tk.RAISED, style='white.TFrame')
        frame = tk.Frame(self, relief=tk.RAISED, bg='white', bd=2)
        frame.place(relwidth=1, relheight=1, bordermode='inside')

        # text_name = '%s\n%s' % (self.room, self.name)
        left, right = self.resize_width()

        # label_name = ttk.Label(frame, text=self.name, style='title.white.TLabel', justify=tk.CENTER)
        label_name = tk.Label(frame, text=self.name, justify=tk.CENTER, bg='white', font=self.font)
        label_name.place(width=left, relheight=1)

        # label_text = ttk.Label(frame, text=self.text, style='title.white.TLabel', wraplength=right)
        label_text = tk.Label(frame, text=self.text, wraplength=right, bg='white', font=self.font,
                              justify=tk.LEFT, anchor=tk.W)
        label_text.place(width=right, relheight=1, x=left)

        if self.hit:
            width = 390-left-right
            self.label_num = tk.Label(frame, textvariable=self.hit_str, anchor=tk.W,
                                      font=self.font_bold, bg='white', fg='red')
            self.label_num.place(width=width, relheight=1, x=left+right)
            self.change_text(self.hit)

    # 窗口宽度定义
    def resize_width(self):
        # font = Font(family='Microsoft YaHei', size=11)
        # room_width = font.measure(self.room)
        name_width = self.font.measure(self.name)

        left_width = name_width+10
        if self.hit:
            right_width = self.font.measure(self.text)+5
        else:
            right_width = 390 - left_width

        text_width = self.font.measure(self.text)
        if text_width > right_width:
            self.height = 50

        return left_width, right_width

    # 动态改变文字
    def change_text(self, value):
        size = 11
        self.hit_str.set(value)
        self.change_font_up(size)

    # 文字变大事件
    def change_font_up(self, size):
        if size < 25:
            size += 2
            self.label_num.config(font=Font(family='Microsoft YaHei', size=size, weight='bold'))
            self.after(10, self.change_font_up, size)
        else:
            self.after(10, self.change_font_down, size)

    # 文字变小事件
    def change_font_down(self, size):
        if size > 11:
            size -= 2
            self.label_num.config(font=Font(family='Microsoft YaHei', size=size, weight='bold'))
            self.after(10, self.change_font_down, size)
