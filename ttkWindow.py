import os
import sys
import tkinter as tk
from tkinter import ttk
from tkinter.font import Font
from tkinter.messagebox import showwarning
from queue import Queue, LifoQueue
from PIL import Image, ImageTk

from room import ChatRoom
from popup_win import LivePopup, StarPopup
from roomInfo import RoomInfo
from Text import BarrageText

star_file = os.path.join(os.getcwd(), 'starList.txt')
if not os.path.exists(star_file):
    with open(star_file, 'w', encoding='utf-8'):
        pass

if getattr(sys, 'frozen', False):
    icon = os.path.join(getattr(sys, '_MEIPASS', '.'), 'icon.ico')
    static_path = os.path.join(getattr(sys, '_MEIPASS', '.'), 'static')
else:
    icon = os.path.join(os.getcwd(), 'icon.ico')
    static_path = os.path.join(os.getcwd(), 'static')


def load_image(path, ins):
    files = os.listdir(path)
    for file in files:
        if file.endswith(('.png', '.gif')):
            img = Image.open(path + '/' + file)
            image = ImageTk.PhotoImage(img)
            ins[file] = image


# 自动窗口缩放事件
def frame_resize(event, frame, size, direction):
    if direction == tk.X:
        frame.config(width=event.width - size)
    elif direction == tk.Y:
        frame.config(height=event.height - size)


class Window:
    popups = []
    gift_popups = {}
    out_ids = {}
    face_img = {}
    static_img = {}
    lv_img = {}

    def __init__(self, master):
        self.master = master
        self.load_static()
        self.position()
        self.lock_text = tk.StringVar()
        self.style()
        self.font = Font(family='Microsoft YaHei', size=11)
        self.window()

    def position(self):
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        x = int(screen_width/2-500)
        y = int(screen_height/2-300)
        self.master.geometry('1000x600+%s+%s' % (x, y))

    def load_static(self):
        load_image(os.path.join(static_path, 'face'), self.face_img)
        load_image(static_path, self.static_img)
        load_image(os.path.join(static_path, 'LV'), self.lv_img)

    # 窗口风格定义
    def style(self):
        s = ttk.Style()
        s.configure('tree.Treeview', font=('Microsoft YaHei', 11))
        s.configure('info.Treeview', font=('Microsoft YaHei', 9))

    # 基础窗口
    def window(self):
        frame = ttk.Frame(self.master)
        frame.pack(expand=1, fill=tk.BOTH)

        frame_left = ttk.Frame(frame)
        frame_left.place(relx=0, rely=0, relheight=1)
        self.window_left(frame_left)

        frame_right = ttk.Frame(frame, width=250)
        # frame_right.grid_propagate(0)
        frame_right.place(anchor=tk.NE, relx=1, rely=0, relheight=1)
        self.window_right(frame_right)
        # self.update()
        frame.bind('<Configure>', lambda x: frame_resize(x, frame_left, 250, tk.X))

    # 左侧弹幕和关注基础窗口
    def window_left(self, frame):
        notebook = ttk.Notebook(frame, padding=(10, 10, 10, 10))

        frame_danmaku = ttk.Frame()
        # self.danmaku_tree = self.tree_view(frame_danmaku, ('昵称', '弹幕'), x=1, y=1, style='tree.Treeview')
        # danmaku_tree.column('等级', width=55, stretch=0)
        # self.danmaku_tree.column('昵称', width=100, stretch=0)
        self.barrage = BarrageText(frame_danmaku, self.static_img, self.lv_img, self.face_img)
        self.barrage.pack(fill=tk.BOTH, expand=1)

        notebook.add(frame_danmaku, text='弹幕')

        frame_star = ttk.Frame()
        self.window_star(frame_star)
        notebook.add(frame_star, text='关注')

        notebook.place(relheight=1, relwidth=1)

        self.lock_button = ttk.Button(frame, textvariable=self.lock_text, width=5)
        self.lock_text.set('锁屏')
        self.lock_button.place(anchor=tk.NE, y=10, relx=0.9)

    # 左侧关注窗口
    def window_star(self, frame):
        frame_top = ttk.Frame(frame)
        frame_top.place(relwidth=1, relheight=0.6, rely=0)

        # self.text_tree = self.tree_view(frame_top, ('时间', '昵称', '直播间', '弹幕'), x=1, y=1, style='tree.Treeview')
        # self.text_tree.column('时间', stretch=0, width=160)
        # self.text_tree.column('昵称', stretch=0, width=100)
        # self.text_tree.column('直播间', stretch=0, width=50)
        self.star_barrage = BarrageText(frame_top, self.static_img, self.lv_img, self.face_img)
        self.star_barrage.pack(fill=tk.BOTH, expand=1)

        frame_bottom = ttk.Frame(frame)
        frame_bottom.place(relwidth=1, relheight=0.4, rely=0.6)

        self.gift_tree = self.tree_view(frame_bottom, ('时间', '昵称', '直播间', '礼物', '连击'), y=1, style='tree.Treeview')
        self.gift_tree.column('时间', stretch=0, width=160)
        self.gift_tree.column('昵称', stretch=0, width=100)
        self.gift_tree.column('直播间', stretch=0, width=50)
        self.gift_tree.column('连击', stretch=0, width=50)

    # 右侧基础窗口
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

    # 主播信息窗口
    def window_info(self, frame):
        info_notebook = ttk.Notebook(frame, padding=(0, 10, 10, 0))

        self.info_tree = ttk.Treeview(columns=('1', '2'), show='tree', style='info.Treeview')
        self.info_tree.column('#0', width=0, stretch=0)
        self.info_tree.column('1', stretch=0, width=80)
        self.info_tree.column('2', stretch=0, width=154)

        info_notebook.add(self.info_tree, text='主播信息：')
        info_notebook.place(relwidth=1, relheight=1)

        self.info_tree.insert('', tk.END, iid='title1', values=('直播间标题：',))
        self.info_tree.insert('', tk.END, iid='title2')
        self.info_tree.insert('', tk.END, iid='name', values=('主播：',))
        self.info_tree.insert('', tk.END, iid='follower', values=('关注：',))
        self.info_tree.insert('', tk.END, iid='weight', values=('体重：',))
        self.info_tree.insert('', tk.END, iid='status', values=('开播状态：',))
        self.info_tree.insert('', tk.END, iid='online', values=('人气：',))
        self.info_tree.insert('', tk.END, iid='start_time', values=('上次直播：',))
        self.info_tree.insert('', tk.END, iid='now_time', values=('更新时间：',))

    # 直播间ID输入窗口
    def window_id(self, frame):
        label = ttk.Label(frame, text='直播间ID：')
        label.place(anchor=tk.NE, relx=0.5, rely=0.1, height=20, relwidth=0.4)

        self.entry_id = ttk.Entry(frame)
        self.entry_id.place(relx=0.5, rely=0.1, height=20, relwidth=0.4)
        self.entry_id.insert(tk.END, '196')

        self.start_button = ttk.Button(frame, text='连接')
        self.start_button.place(anchor=tk.NE, relx=0.4, rely=0.5, width=60)
        self.stop_button = ttk.Button(frame, text='断开连接', state=tk.DISABLED)
        self.stop_button.place(relx=0.6, rely=0.5, width=60)

    # 关注列表设置窗口
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

        self.save_button = ttk.Button(frame, text='保存', width=5)
        self.save_button.place(anchor=tk.NE, relx=0.6, rely=0)
        self.reload_button = ttk.Button(frame, text='更新', width=5)
        self.reload_button.place(anchor=tk.NE, relx=0.8, rely=0)

    # 表格视图创建
    def tree_view(self, frame, columns, x=None, y=None, style='Treeview'):
        tree = ttk.Treeview(frame, columns=columns, show='headings', style=style)
        if x:
            xbar = ttk.Scrollbar(frame, orient=tk.HORIZONTAL, command=tree.xview)
            tree.config(xscrollcommand=xbar.set)
            xbar.pack(fill=tk.X, side=tk.BOTTOM)
        if y:
            ybar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
            tree.config(yscrollcommand=ybar.set)
            ybar.pack(fill=tk.Y, side=tk.RIGHT)

        for idx, col in enumerate(columns):
            tree.heading(idx, text=col)

        tree.pack(fill=tk.BOTH, expand=1)
        return tree

    # 表格插入并按文字长度调整格宽
    def insert(self, tree, values):
        for idx, value in enumerate(values):
            value = str(value).replace('\n', ' ')
            values[idx] = value
            text_w = self.font.measure(value)
            if tree.column(idx, width=None) < text_w:
                tree.column(idx, width=text_w + 10)
        iid = tree.insert('', tk.END, values=values)
        return iid

    def insert_title(self, title):
        font = Font(family='Microsoft YaHei', size=9)
        title1 = title
        length = len(title)
        width = self.info_tree.column('2', width=None)-10
        title_width = font.measure(title)
        while title_width > width:
            length -= 1
            title1 = title[:length]
            title_width = font.measure(title1)

        self.insert_info('title1', title1)
        self.insert_info('title2', title[length:])

    def insert_info(self, iid, value):
        self.info_tree.set(iid, column='2', value=value)

    # 开播提醒弹出窗口
    def live_popup(self, room, image, title, status, name):
        popup = LivePopup(room, image, title, status, name)
        for win in self.popups:
            win.move_up(popup.height)
        popup.pop_up()
        self.popups.append(popup)
        self.master.after(5000, self.fade_out, popup)

    # 关注提醒弹出窗口
    def star_popup(self, name, text):
        popup = StarPopup(name, text)
        for win in self.popups:
            win.move_up(popup.height)
        popup.pop_up()
        self.popups.append(popup)
        self.master.after(8000, self.fade_out, popup)

    # 礼物提醒弹出窗口
    def gift_popup(self, name, text, gift_id, hit):
        gift_str = None
        if gift_id:
            gift_str = name + gift_id
        if gift_str in self.gift_popups.keys():
            popup = self.gift_popups[gift_str]
            popup.change_text(hit)
            self.master.after_cancel(self.out_ids[gift_str])
            out_id = self.master.after(5000, self.fade_out, popup, gift_str)
            self.out_ids[gift_str] = out_id
        else:
            popup = StarPopup(name, text, hit=hit)
            for win in self.popups:
                win.move_up(popup.height)
            popup.pop_up()
            self.popups.append(popup)
            self.gift_popups[gift_str] = popup
            out_id = self.master.after(5000, self.fade_out, popup, gift_str)
            self.out_ids[gift_str] = out_id

    # 窗口淡出
    def fade_out(self, win, gift_str=None):
        if gift_str:
            del self.gift_popups[gift_str], self.out_ids[gift_str]
        win.pop_down()
        idx = self.popups.index(win)
        if idx > 0:
            for i in range(0, idx):
                self.popups[i].move_down(win.height)
        self.popups.remove(win)


class App(Window):
    CheckVar = True
    starList = []
    num = 0
    room = None     # 当前房间ID
    live = False    # 开播状态
    title = None    # 直播间标题

    def __init__(self, master):
        super(App, self).__init__(master)
        self.master = master
        self.master.iconbitmap(icon)
        self.add_event()
        self.result_q = Queue()
        self.gift_q = LifoQueue()
        self.info_q = LifoQueue()
        self.read_stars()

    def add_event(self):
        self.lock_button.configure(command=self.lock)
        self.start_button.configure(command=self.on)
        self.stop_button.configure(command=self.off)
        self.save_button.configure(command=self.save_stars)
        self.reload_button.configure(command=self.read_stars)
        self.master.bind('<<MESSAGE>>', self._handle_message)
        self.master.bind('<<ROOMINFO>>', self._handle_roomInfo)

    # 开始连接事件
    def on(self):
        room_id = self.entry_id.get()
        if not room_id.isdigit():
            showwarning('直播间ID不正确', '请输入正确的直播间ID！')
        else:
            if room_id != self.room:
                self.title = None
                self.room = room_id
                self.barrage.delete(1.0, tk.END)
                self.num = 0
            self.update_danmaku(room_id)
            self.update_info(room_id)
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.ACTIVE)

    def update_danmaku(self, room_id):
        self.app = ChatRoom(room_id, self.result_q, self.gift_q, self.master)
        self.app.setDaemon(True)
        self.app.start()

    def update_info(self, room_id):
        self.info = RoomInfo(room_id, self.gift_q, self.info_q, self.master)
        self.info.setDaemon(True)
        self.info.start()

    # 断开连接事件
    def off(self):
        self.app.quit()
        self.info.quit()
        self.start_button.config(state=tk.ACTIVE)
        self.stop_button.config(state=tk.DISABLED)

    # 滚屏锁屏事件
    def lock(self):
        if self.CheckVar:
            self.CheckVar = False
            self.lock_text.set('滚屏')
        else:
            self.CheckVar = True
            self.lock_text.set('锁屏')

    # 房间信息处理
    def _handle_roomInfo(self, event):
        room_info = self.info_q.get()
        room_id = room_info['room_id']
        name = room_info['owner_name']

        title = room_info['room_name']
        if self.title and title != self.title:
            self.star_popup('%s改标题了' % name, title)
        self.title = title
        self.insert_title(title)

        status = room_info['room_status']
        if status == '2':
            status = '下播了'
            if self.live:
                self.live = False
        elif status == '1':
            status = '直播中（已播%s分钟）' % room_info['minutes']
            if not self.live:
                image = os.path.join(os.getcwd(), 'room_%s.jpg' % room_id)
                self.live_popup(room_id, image, title, status, name)
                self.live = True

        self.insert_info('name', name)
        self.insert_info('follower', room_info['fans_num'])
        self.insert_info('weight', room_info['owner_weight'])
        self.insert_info('status', status)
        self.insert_info('online', room_info['online'])
        self.insert_info('start_time', room_info['start_time'])
        self.insert_info('now_time', room_info['now_time'])

    # 消息处理
    def _handle_message(self, event):
        message = self.result_q.get()
        msg_type = message.attr('type')
        name = message.attr('nn')
        if msg_type in ('con_error', 'loginres'):
            self._update_danmaku(message, insert=1)

        elif msg_type == 'chatmsg':
            tag = None
            if name in self.starList:
                tag = 1
                self._update_star_danmaku(message)
                self.star_popup(name, message.attr('txt'))

            self._update_danmaku(message, tag)

        elif msg_type == 'uenter':
            if name in self.starList:
                self._update_star_danmaku(message, enter=1)
                self.star_popup(name, message.attr('txt'))

        elif msg_type in ('dgb', 'bc_buy_deserve', 'spbc'):
            if name in self.starList:
                txt = '赠送 %s %s' % (message.attr('dn'), message.attr('gift'))
                self._update_gift([message.attr('time'), name, message.attr('room'), txt, message.attr('hits')])
                self.gift_popup(name, txt, message.attr('gift'), message.attr('hits'))

        elif msg_type in ('ggbb', 'gpbc'):
            if name in self.starList:
                txt = '抢了%s的%s个%s' % (message.attr('dn'), message.attr('num'), message.attr('gift'))
                self._update_gift([message.attr('time'), name, message.attr('room'), txt])
                self.star_popup(name, txt)

    # 更新全部弹幕
    def _update_danmaku(self, msg, tag=None, insert=None):
        if self.num < 3000:
            self.num += 1
        else:
            self.barrage.delete(1.0, 2.0)
        if insert:
            self.barrage.insert(tk.END, msg.attr('txt'))
        else:
            self.barrage.handle_message(msg, tag)
        if self.CheckVar:
            self.barrage.see(tk.END)
        self.barrage.insert(tk.END, '\n')

    # 更新关注人弹幕
    def _update_star_danmaku(self, msg, enter=None):
        self.star_barrage.insert(tk.END, msg.attr('time')+' ')
        if enter:
            self.star_barrage.insert(tk.END, msg.attr('nn')+msg.attr('txt'))
        else:
            self.star_barrage.handle_message(msg)
        if self.CheckVar:
            self.star_barrage.see(tk.END)
        self.star_barrage.insert(tk.END, '\n')

    # 更新关注人礼物
    def _update_gift(self, values):
        idd = self.insert(self.gift_tree, values)
        if self.CheckVar:
            self.gift_tree.see(idd)

    # 从文件读取关注列表
    def read_stars(self):
        self.stars.delete(1.0, tk.END)
        with open(star_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines:
                self.starList.append(line.strip())
                self.stars.insert(tk.END, line)

    # 把关注列表存入文件
    def save_stars(self):
        text = self.stars.get(1.0, tk.END)
        with open(star_file, 'w', encoding='utf-8') as f:
            for star in text.split('\n'):
                if star.strip():
                    f.write(star.strip() + '\n')
        self.read_stars()
