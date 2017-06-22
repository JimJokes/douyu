import os
import sys
import tkinter as tk
from tkinter import ttk
from tkinter.font import Font
from tkinter.messagebox import showwarning

import utils
from popup_win import LivePopup, StarPopup
from dammu import Danmu

star_file = os.path.join(os.getcwd(), 'starList.txt')

if getattr(sys, 'frozen', False):
    icon = os.path.join(getattr(sys, '_MEIPASS', '.'), 'icon.ico')
else:
    icon = os.path.join(os.getcwd(), 'icon.ico')


# 自动窗口缩放事件
def frame_resize(event, frame, size, direction):
    if direction == tk.X:
        frame.config(width=event.width - size)
    elif direction == tk.Y:
        frame.config(height=event.height - size)


class Window(tk.Tk):
    popups = []
    gift_popups = {}
    out_ids = {}

    def __init__(self, *args, **kwargs):
        super(Window, self).__init__(*args, **kwargs)
        self.lock_text = tk.StringVar()
        self.style()
        self.font = Font(family='Microsoft YaHei', size=11)
        self.window()
        self.read_stars()

    # 窗口风格定义
    def style(self):
        s = ttk.Style()
        s.configure('tree.Treeview', font=('Microsoft YaHei', 11))

    # 基础窗口
    def window(self):
        frame = ttk.Frame()
        frame.pack(expand=1, fill=tk.BOTH)

        frame_left = ttk.Frame(frame)
        frame_left.place(relx=0, rely=0, relheight=1)
        self.window_left(frame_left)

        frame_right = ttk.Frame(frame, width=250)
        frame_right.grid_propagate(0)
        frame_right.place(anchor=tk.NE, relx=1, rely=0, relheight=1)
        self.window_right(frame_right)
        # self.update()
        frame.bind('<Configure>', lambda x: frame_resize(x, frame_left, 250, tk.X))

    # 左侧弹幕和关注基础窗口
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

    # 左侧关注窗口
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

    # 直播间ID输入窗口
    def window_id(self, frame):
        label = ttk.Label(frame, text='直播间ID：')
        label.place(anchor=tk.NE, relx=0.5, rely=0.1, height=20, relwidth=0.4)

        self.entry_id = ttk.Entry(frame)
        self.entry_id.place(relx=0.5, rely=0.1, height=20, relwidth=0.4)

        self.start_button = ttk.Button(frame, text='连接', command=self.on)
        self.start_button.place(anchor=tk.NE, relx=0.4, rely=0.5, width=60)
        self.stop_button = ttk.Button(frame, text='断开连接', state=tk.DISABLED, command=self.off)
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

        save_button = ttk.Button(frame, text='保存', width=5, command=self.star_popup)
        save_button.place(anchor=tk.NE, relx=0.6, rely=0)
        reload_button = ttk.Button(frame, text='更新', width=5, command=self.gift_popup)
        reload_button.place(anchor=tk.NE, relx=0.8, rely=0)

    # 表格视图创建
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

    # 表格插入并按文字长度调整格宽
    def insert(self, tree, values):
        for idx, value in enumerate(values):
            value = value.replace('\n', '')
            text_w = self.font.measure(value)
            if tree.column(tree.columns[idx], width=None) < text_w:
                tree.column(tree.columns[idx], width=text_w + 10)
        tree.insert('', tk.END, values=values)

    # 开始连接事件
    def on(self):
        room_id = self.entry_id.get()
        if not room_id.isdigit():
            showwarning('直播间ID不正确', '请输入正确的直播间ID！')
        else:
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.ACTIVE)

    # 断开连接事件
    def off(self):
        self.start_button.config(state=tk.ACTIVE)
        self.stop_button.config(state=tk.DISABLED)

    # 滚屏锁屏事件
    def lock(self):
        if utils.CheckVar:
            utils.CheckVar = False
            self.lock_text.set('滚屏')
        else:
            utils.CheckVar = True
            self.lock_text.set('锁屏')

    # 从文件读取关注列表
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

    # 把关注列表存入文件
    def save_stars(self):
        text = self.stars.get(1.0, tk.END)
        with open(star_file, 'w', encoding='utf-8') as f:
            for star in text.split('\n'):
                if star.strip():
                    f.write(star.strip()+'\n')
        self.read_stars()

    # 开播提醒弹出窗口
    def live_popup(self, room=123, image='196_170622002601.jpg', title='湖大覅就阿发回答UI覅哈吉会法界会好打法鸡从女子见覅哦啊发', status='直播中（已播112分钟）', name='123'):
        popup = LivePopup(room, image, title, status, name)
        for win in self.popups:
            win.move_up(popup.height)
        popup.pop_up()
        self.popups.append(popup)
        self.after(5000, self.fade_out, popup)

    # 关注提醒弹出窗口
    def star_popup(self, room=123, name='讲哦发哈斯蒂芬', text='加个我哦啊大风会哦个'):
        popup = StarPopup(room, name, text)
        for win in self.popups:
            win.move_up(popup.height)
        popup.pop_up()
        self.popups.append(popup)
        self.after(8000, self.fade_out, popup)

    # 礼物提醒弹出窗口
    def gift_popup(self, room=123, name='和覅哦啊积分ID', text='我就热哦啊的房间啊', gift_id='123', hit='23'):
        gift_str = name + gift_id
        if gift_str in self.gift_popups.keys():
            popup = self.gift_popups[gift_str]
            popup.change_text(hit)
            self.after_cancel(self.out_ids[gift_str])
            out_id = self.after(8000, self.fade_out, popup, gift_str)
            self.out_ids[gift_str] = out_id
        else:
            popup = StarPopup(room, name, text, hit=hit)
            for win in self.popups:
                win.move_up(popup.height)
            popup.pop_up()
            self.popups.append(popup)
            self.gift_popups[gift_str] = popup
            out_id = self.after(8000, self.fade_out, popup, gift_str)
            self.out_ids[gift_str] = out_id

    # 窗口淡出
    def fade_out(self, win, gift_str=None):
        if gift_str:
            self.gift_popups.pop(gift_str)
            self.out_ids.pop(gift_str)
        win.pop_down()
        idx = self.popups.index(win)
        if idx > 0:
            for i in range(0, idx):
                self.popups[i].move_down(win.height)
        self.popups.remove(win)


if __name__ == '__main__':
    app = Window()
    app.geometry('1000x600+300+150')
    app.mainloop()
    # top = tk.Tk()
    # app = LivePopup(top)
    # app.popup()
    # app1 = StarPopup(top)
    # app1.popup()
    # app.move_up(app1.height)
    # top.mainloop()
    # top = tk.Tk()
    # title = ttk.Label()
    # print(title.winfo_class())
    # top.destroy()
    # top.mainloop()
