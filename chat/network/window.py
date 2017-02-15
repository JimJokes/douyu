import tkinter as tk
import time, asyncio
from tkinter.scrolledtext import *
from tkinter.constants import END
from chat.room import ChatRoom
from queue import Queue


class View(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.pack(padx='40', pady='10')
        self.window()

    def window(self):
        t = tk.Label(self, text='输入直播间号：')
        t.grid(row=0, column=0, pady='10')
        self.room = tk.Entry(self, width='10')
        self.room.grid(row=0, column=1)
        b = tk.Button(self, text="开始", command=self.new_window)
        b.grid(row=2, column=0, ipadx='20', pady='10')
        d = tk.Button(self, text='退出', command=self.quit)
        d.grid(row=2, column=1, ipadx='20')

    def new_window(self):
        room_id = self.room.get()
        window = tk.Toplevel(self)
        label = tk.Label(window, text=room_id)
        label.grid(row=0, column=0)
        self.text = ScrolledText(window)
        self.text.grid(row=1, ipadx='100', ipady='100')
        b = tk.Button(window, text='开始', command=self.no)
        b.grid(row=0, column=1)
        # message = await alldanmu(room_id)
        # self.text.insert(END, message + '\n')
        # self.update()

    async def go(self):
        room = self.room.get()
        message = await alldanmu(room)
        self.text.insert(END, message+'\n')
        self.update()

    def no(self):
        for i in range(20):
            self.text.insert(END, i)
            self.text.update()
            time.sleep(10)


def alldanmu(_roomid):
    _room = ChatRoom(_roomid)
    # _room.on('chatmsg', on_chat_message)
    # _room.on('uenter', on_chat_message)
    yield '开始监控[%s]的直播间弹幕！' % rooms[_roomid]
    for msg in _room.knock():
        try:
            msg_type = msg.attr('type')
            now = time.strftime("%y-%m-%d %H:%M:%S", time.localtime())
            _roomid = msg.attr('rid')
            _uname = msg.attr('nn')
            _ct = msg.attr('ct')
            if _ct is None:
                _ct = '网页'
            else:
                _ct = '手机'

            if msg_type == 'chatmsg':
                message = '%s [%s]:[%s][%s][等级:%s]:%s' % (now, rooms[_roomid], _ct, _uname, msg.attr('level'), msg.attr('txt'))
                yield message
            elif msg_type == 'uenter':
                message = '%s [%s]:[%s][等级:%s] 进入了直播间!' % (now, rooms[_roomid], _uname, msg.attr('level'))
                yield message

        except KeyError:
            continue


def on_chat_message(msg):
    now = time.strftime("%y-%m-%d %H:%M:%S", time.localtime())
    _roomid = msg.attr('rid')
    _uname = msg.attr('nn')
    _ct = msg.attr('ct')
    if _ct is None:
        _ct = '网页'
    else:
        _ct = '手机'

    if msg.attr('type') == 'chatmsg':
        message = '%s [%s]:[%s][%s][等级:%s]:%s' % (now, rooms[_roomid], _ct, _uname, msg.attr('level'), msg.attr('txt'))
    else:
        message = '%s [%s]:[%s][等级:%s] 进入了直播间!' % (now, rooms[_roomid], _uname, msg.attr('level'))
    return message

rooms = {
        '196': '小缘',
        '160141': '小白脸',
        '229346': '钱佳',
        '283566': '皮皮虾',
        '60937': '炸得',
        '13703': '火焰鼠',
        '22': '时光机'
    }

if __name__ == "__main__":
    root = View()
    root.master.title('斗鱼弹幕姬')
    root.master.resizable(False, False)
    root.mainloop()
