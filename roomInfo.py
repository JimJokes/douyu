import os
import time
import asyncio
import aiohttp
import threading
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
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.init())
        loop.close()

    async def init(self):
        while self.alive.is_set():
            async with aiohttp.ClientSession() as session:
                res_room = await self.update_info(session)
                res_gift = await self.update_gift(session)

                if res_room and res_room['error'] == 0:
                    await self._handle_info(res_room, session)

                if res_gift and res_gift['error'] == 0:
                    gifts_info = res_gift['data']['prop_gift']
                    try:
                        gifts_info.extend(res_room['data']['gift'])
                    except (KeyError, TypeError):
                        pass
                    for gift in gifts_info:
                        self.gifts[gift['id']] = gift['name']
                    self.gift_q.put(self.gifts)

            time.sleep(10)

        # loop.stop()

    async def _handle_info(self, res, session):
        now = time.localtime()
        room_info = res['data']
        for key in self.status:
            if key == 'now_time':
                self.status[key] = time.strftime('%Y-%m-%d %H:%M:%S', now)
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
        self.info_q.put(self.status)
        try:
            self.root.event_generate('<<ROOMINFO>>')
        except RuntimeError:
            pass

    async def update_info(self, session):
        try:
            res = await fetch_json(session, self.room_api)
            return res
        except Exception as e:
            logger.exception(e)
            return None

    async def update_gift(self, session):
        try:
            res = await fetch_json(session, GIFT_API)
            return res
        except Exception as e:
            logger.exception(e)
            return None

    async def update_pic(self, session, url):
        if url == self.status['room_thumb']:
            pass
        else:
            try:
                res = await fetch_read(session, url)
                with open(self.room_thumb, 'wb') as f:
                    f.write(res)
            except Exception as e:
                logger.exception(e)
        return url

    def quit(self):
        self.alive.clear()


async def fetch_json(session, url):
    async with session.get(url) as res:
        return await res.json()

async def fetch_read(session, url):
    async with session.get(url) as res:
        return await res.read()
