import json
import time
import threading
import urllib.request
from http.client import IncompleteRead
from urllib.error import URLError
import html as HTML

import utils
import logging
logger = logging.getLogger('main.'+__name__)

gift_api = 'https://capi.douyucdn.cn/api/v1/station_effect'
room_url = 'https://www.douyu.com/196'


class RoomInfo(threading.Thread):
    def __init__(self, room_id, *args):
        super(RoomInfo, self).__init__()
        self.status = {
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
        }
        self.room_id = room_id
        self.args = args
        self.stop = False

    def run(self):
        room_api = 'http://open.douyucdn.cn/api/RoomApi/room/%s' % self.room_id
        while True:
            if self.stop:
                raise SystemExit

            try:
                with urllib.request.urlopen(room_api) as f:
                    html = f.read().decode('utf-8')

                room_info = json.loads(html)['data']
                gift_info = room_info['gift']
                for k in self.status:
                    self.status[k] = room_info[k]
                for gift in gift_info:
                    utils.gifts[gift['id']] = gift['name']
            except (IncompleteRead, URLError, ConnectionRefusedError, ConnectionResetError):
                time.sleep(1)
                continue
            except Exception as e:
                logger.exception(e)
                time.sleep(1)
                continue

            try:
                with urllib.request.urlopen(gift_api) as f:
                    html = f.read().decode('utf-8')

                gifts_info = json.loads(html)['data']['prop_gift']
                for gift in gifts_info:
                    utils.gifts[gift['id']] = gift['name']

                now = time.localtime()
                now_str = time.strftime('%Y-%m-%d %H:%M:%S', now)

                if self.status['room_status'] == '2':
                    self.status['room_status'] = '下播了'
                elif self.status['room_status'] == '1':
                    start = self.status['start_time']
                    start = time.strptime(start, '%Y-%m-%d %H:%M')
                    minute = int((time.mktime(now)-time.mktime(start))/60)
                    self.status['room_status'] = '直播中(已播%s分钟)' % minute
            except (IncompleteRead, URLError, ConnectionRefusedError, ConnectionResetError):
                time.sleep(1)
                continue
            except Exception as e1:
                logger.exception(e1)
                time.sleep(1)
                continue

            str_1, str_2, str_3, str_4, str_5, str_6, str_7, str_8 = self.args
            str_1.set(HTML.unescape(self.status['room_name']))
            str_2.set(self.status['owner_name'])
            str_3.set(self.status['room_status'])
            str_4.set(self.status['fans_num'])
            str_5.set(self.status['owner_weight'])
            str_6.set(self.status['online'])
            str_7.set(self.status['start_time'])
            str_8.set(now_str)

            time.sleep(30)
