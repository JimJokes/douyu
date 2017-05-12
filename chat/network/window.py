import tkinter as tk
import time, threading

from tkinter.scrolledtext import *
from tkinter.constants import END

from chat.network.utils import align_right
from chat.room import ChatRoom


class View(tk.Frame):
    def __init__(self, master=None):
        super(View, self).__init__(master)
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
        self.text.grid(row=1, ipadx='200', ipady='200')
        self.go()
        # b = tk.Button(window, text='开始', command=self.go)
        # b.grid(row=0, column=1)
        # message = await alldanmu(room_id)
        # self.text.insert(END, message + '\n')
        # self.update()

    def go(self):
        room = self.room.get()
        dammu = Danmu(self.text, room)
        dammu.start()


class Danmu(threading.Thread):
    def __init__(self, text, roomid):
        super(Danmu, self).__init__()
        self.text = text
        self._roomid = roomid

    def run(self):
        _room = ChatRoom(self._roomid)
        # _room.on('chatmsg', on_chat_message)
        # _room.on('uenter', on_chat_message)
        self.text.insert(END, '开始监控[%s]的直播间弹幕！\n' % self._roomid)
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
                    message = align_right('%s [%s] %s' % (now, _ct, _uname), 50) + ':%s' % msg.attr('txt')
                    self.text.insert(END, message + '\n')
                    self.text.see(END)
                # elif msg_type == 'uenter':
                #     message = '%s [%s]:[%s][等级:%s] 进入了直播间!' % (now, rooms[_roomid], _uname, msg.attr('level'))
                #     yield message

            except KeyError:
                continue


if __name__ == "__main__":
    root = View()
    root.master.title('斗鱼弹幕姬')
    # root.master.resizable(False, False)
    root.mainloop()
