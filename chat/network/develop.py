from tkinter.scrolledtext import ScrolledText

from chat.room import ChatRoom
from chat.network.utils import *
from chat.network.client import Client
import time, threading
import tkinter as tk


def keep_alive(client, delay):
    while True:
        current_ts = int(time.time())
        client.send({
            'type': 'keeplive',
            'tick': current_ts
        })
        time.sleep(delay)


def rsv(s, room_id):
    for message in s.receive():
        if not message:
            continue

        msg_type = message.attr('type')
        if msg_type == 'loginres':
            try:
                s.send({'type': 'joingroup', 'rid': room_id, 'gid': '-9999'})
                # print('已连接到弹幕服务器，房间id：%s' % room_id)
            except Exception as e:
                print(e)
        # elif msg_type == 'chatmsg':
        print('\033[33m')
        print(message.body)
        print('\033[0m' + '\n')


# def unescape(value):
#     # value = str(value)
#     value = value.replace(b'@S', b'/')
#     value = value.replace(b'@A', b'@')
#     return value

def start():
    room_id = '196'
    s = Client()
    s.send({'type': 'loginreq', 'roomid': room_id})

    app = threading.Thread(target=keep_alive, args=(s, 45))
    app.start()
    rsv(s, room_id)


widths = [
    (126,   1), (159,   0), (687,   1), (710,   0), (711,   1),
    (727,   0), (733,   1), (879,   0), (1154,  1), (1161,  0),
    (4347,  1), (4447,  2), (7467,  1), (7521,  0), (8369,  1),
    (8426,  0), (9000,  1), (9002,  2), (11021, 1), (12350, 2),
    (12351, 1), (12438, 2), (12442, 0), (19893, 2), (19967, 1),
    (55203, 2), (63743, 1), (64106, 2), (65039, 1), (65059, 0),
    (65131, 2), (65279, 1), (65376, 2), (65500, 1), (65510, 2),
    (120831, 1), (262141, 2), (1114109, 1),
]


def get_width(o):
    """Return the screen column width for unicode ordinal o."""
    global widths
    if o == 0xe or o == 0xf:
        return 0
    for num, wid in widths:
        if o <= num:
            return wid
    return 1


def is_full_width(char):
    if char >= u'\u4e00' and char <= u'\u9fa5':
        return True
    else:
        return False


def align_right(text, width):
    count = 0
    for char in text:
        code = ord(char)
        if get_width(code) == 2:
            count += 2
        elif get_width(code) == 1:
            count += 1
        else:
            continue
    return text + ' ' * (width - count)


class Page(tk.Frame):
    def __init__(self, master=None):
        super(Page, self).__init__(master)
        self.pack(padx=500, pady=300)
        self.window()

    def window(self):
        frame_left = tk.LabelFrame(text='全部弹幕：', padx=10, pady=10)
        frame_left.place(relwidth=0.5, relheight=1)

        text_damnu = ScrolledText(frame_left)
        text_damnu.place(relwidth=1, relheight=1)

        frame_right = tk.Frame(relief=tk.FLAT)
        frame_right.place(relwidth=0.5, relheight=1, relx=0.5)

        frame_star = tk.LabelFrame(frame_right, text='关注列表：(一行一个ID)', padx=10, pady=10)
        frame_star.place(relwidth=0.5, relheight=0.3)
        text_star = ScrolledText(frame_star)
        text_star.place(relwidth=0.8, relheight=1)
        button_star = tk.Button(frame_star, text='确定')
        button_star.place(anchor=tk.NE, relx=1, height=22, rely=0)

        frame_id = tk.Frame(frame_right, relief=tk.FLAT)
        frame_id.place(relwidth=0.5, relheight=0.1, rely=0.3)
        label_1 = tk.Label(frame_id, text='直播间ID：')
        label_1.place(anchor=tk.NE, relx=0.5, rely=0.1, height=17, relwidth=0.5)
        entry_id = tk.Entry(frame_id)
        entry_id.insert(tk.END, '196')
        entry_id.place(relx=0.5, rely=0.1, height=17, relwidth=0.4)
        button_start = tk.Button(frame_id, text='连接')
        button_start.place(anchor=tk.NE, relx=0.4, rely=0.6, width=55, height=22)
        button_stop = tk.Button(frame_id, text='断开连接')
        button_stop.place(relx=0.6, rely=0.6, width=55, height=22)

        frame_info = tk.LabelFrame(frame_right, text='主播信息：')
        frame_info.place(relx=0.5, relwidth=0.5, relheight=0.4)

        frame_star_danmu = tk.LabelFrame(frame_right, text='关注内容：', padx=10, pady=10)
        frame_star_danmu.place(rely=0.4, relwidth=1, relheight=0.6)
        text_star_danmu = ScrolledText(frame_star_danmu)
        text_star_danmu.place(relwidth=1, relheight=1)



class No(threading.Thread):
    def __init__(self, text):
        super(No, self).__init__()
        self.text = text
        # self.text = ScrolledText()

    def run(self):
        j = 0
        for i in range(1000):
            self.text.insert(tk.END, 'hiohohioho '+str(i) + '\n')
            if j > 19:
                self.text.delete(1.0, 2.0)
            else:
                j += 1
            y = self.text.vbar.get()[1]
            if y > 0.96:
                self.text.see(tk.END)
            time.sleep(0.5)


if __name__ == '__main__':
    app = Page()
    app.master.title('斗鱼弹幕姬')
    app.mainloop()
