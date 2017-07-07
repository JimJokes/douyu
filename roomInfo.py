import os
import time
import asyncio
from tkinter import Tk

import aiohttp
import threading
import requests
from html import unescape

import logging
logger = logging.getLogger('main.'+__name__)

GIFT_API = 'https://capi.douyucdn.cn/api/v1/station_effect'
ROOM_API = 'http://open.douyucdn.cn/api/RoomApi/room/%s'


class RoomInfo(threading.Thread):
    status = {
        'now_time': None,
        'room_id': None,
        'room_name': None,
        'owner_name': None,
        'avatar': None,
        'owner_weight': None,
        'room_thumb': None,
        'room_status': None,
        'start_time': None,
        'fans_num': None,
        'online': None,
        'minutes': None,
    }
    gifts = {}

    def __init__(self, room_id, gift_q, info_q, root):
        super(RoomInfo, self).__init__()
        self.room_id = room_id
        self.room_api = ROOM_API % self.room_id
        self.room_thumb = os.path.join(os.getcwd(), 'room_%s.jpg' % self.room_id)
        self.gift_q = gift_q
        self.info_q = info_q
        self.root = root
        self.alive = threading.Event()
        self.alive.set()

    def run(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.init(loop))
        loop.run_forever()
        loop.close()

    async def init(self, loop):
        while self.alive:
            async with aiohttp.ClientSession() as session:
                room_info = await self.update_info(session)
                gifts_info = await self.update_gift(session)
                now = time.localtime()

                for key in self.status:
                    if key == 'now_time':
                        self.status[key] = time.strftime('%m-%d %H:%M:%S', now)
                    elif key == 'room_thumb':
                        self.status[key] = await self.update_pic(session, room_info['room_thumb'])
                    elif key == 'room_name':
                        self.status[key] = unescape(room_info[key])
                    elif key == 'minutes' and room_info['room_status'] == '1':
                        start = room_info['start_time']
                        start = time.strptime(start, '%Y-%m-%d %H:%M')
                        minutes = int((time.mktime(now) - time.mktime(start)) / 60)
                        self.status[key] = minutes
                    elif key == 'minutes':
                        pass
                    else:
                        self.status[key] = room_info[key]

                gifts_info.extend(room_info['gift'])
                for gift in gifts_info:
                    self.gifts[gift['id']] = gift['name']

            self.info_q.put(self.status)
            self.root.event_generate('<<ROOMINFO>>')
            self.gift_q.put(self.gifts)
            time.sleep(10)

        loop.stop()

    async def update_info(self, session):
        res = await fetch_json(session, self.room_api)
        room_info = res['data']
        return room_info

    async def update_gift(self, session):
        res = await fetch_json(session, GIFT_API)
        gift_info = res['data']['prop_gift']
        return gift_info

    async def update_pic(self, session, url):
        if url == self.status['room_thumb']:
            pass
        else:
            res = await fetch_read(session, url)
            with open(self.room_thumb, 'wb') as f:
                f.write(res)
        return url

    def quit(self):
        self.alive.clear()


async def fetch_json(session, url):
    async with session.get(url) as res:
        return await res.json()

async def fetch_read(session, url):
    async with session.get(url) as res:
        return await res.read()
