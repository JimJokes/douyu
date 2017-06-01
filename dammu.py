import threading
from tkinter import END, TclError

import time
import sys

import utils
from room import ChatRoom, KeepAlive, KEEP_ALIVE_INTERVAL_SECONDS
from logger import Logger
logger = Logger(__name__)
non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode+1), 0xfffd)


class Danmu(threading.Thread):
    def __init__(self, text, text_star, roomid):
        super(Danmu, self).__init__()
        self.text = text
        self.text_star = text_star
        self._roomid = roomid
        self.stop = False

    def run(self):
        self._room = ChatRoom(self._roomid)
        for mess in self._room.connect():
            message = '连接弹幕服务器出错，请重新连接！'
            self.update_danmu(message)
        self.app = KeepAlive(self._room.client, KEEP_ALIVE_INTERVAL_SECONDS)
        self.app.setDaemon(True)
        self.app.start()

        self.text.insert(END, '开始监控[%s]的直播间弹幕！\n' % self._roomid)
        for msg in self._room.knock():
            if self.stop:
                self._room.cutoff()
                self.app.stop = True
                raise SystemExit
            try:
                msg_type = msg.attr('type')

                if msg_type == 'error' and msg.attr('code') == '2000':
                    message = '连接弹幕服务器出错，请重新连接！'
                    self.update_danmu(message)

                if msg_type == 'chatmsg':
                    # _ct = msg.attr('ct')
                    # if _ct is None:
                    #     _ct = '网页'
                    # else:
                    #     _ct = '手机'
                    _uname = msg.attr('nn')
                    _lv = msg.attr('level')
                    message = utils.align_right('[LV:%s] ' % _lv, 9) + utils.align_right('%s' % _uname, 21) + ':%s' % msg.attr('txt')
                    if _uname in utils.stars:
                        mess = '[LV:%s] %s :%s' % (_lv, _uname, msg.attr('txt'))
                        self.update_star(mess)
                    self.update_danmu(message)

                if msg_type == 'uenter':
                    _uname = msg.attr('nn')
                    if _uname in utils.stars:
                        message = '%s 进入了直播间！' % _uname
                        self.update_star(message)

                if msg_type == 'dgb' or msg_type == 'bc_buy_deserve':
                    _uname = msg.attr('nn') or msg.attr('sui')['nick']
                    if _uname in utils.stars:
                        giftid = msg.attr('gfid')
                        hit = msg.attr('hits') or 1
                        if giftid:
                            try:
                                gift = utils.gifts[giftid]
                            except KeyError:
                                gift = '未知礼物%s' % giftid
                            message = '%s 送出了 %s, 连击X %s' % (_uname, gift, hit)
                        else:
                            lev = msg.attr('lev')
                            cq = utils.cq[lev]
                            message = '%s 送出了 %s, 连击X %s' % (_uname, cq, hit)
                        self.update_star(message)

            except KeyError:
                continue

    def update_danmu(self, message):
        try:
            self.text.insert(END, message + '\n')
        except TclError:
            self.text.insert(END, message.translate(non_bmp_map)+'\n')
            # print(message)
        except Exception as e:
            logger.exception(e)
            return
        if utils.j > 2999:
            self.text.delete(1.0, 2.0)
        else:
            utils.j += 1
        if utils.CheckVar:
            self.text.see(END)

    def update_star(self, message):
        now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        try:
            self.text_star.insert(END, now+' '+message + '\n')
        except TclError:
            self.text_star.insert(END, now+' '+message.translate(non_bmp_map)+'\n')
        except Exception as e:
            logger.exception(e)
            return
        if utils.i > 999:
            self.text_star.delete(1.0, 2.0)
        else:
            utils.i += 1
        if utils.CheckVar:
            self.text_star.see(END)

    def delete_danmu(self):
        self.text.delete(1.0, END)
        utils.j = 0
