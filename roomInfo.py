import json
import threading, urllib.request, logging
logging.basicConfig(filename='error.log', level=logging.DEBUG,
                    format='%(asctime)s %(filename)s[line:%(lineno)s] %(levelname)s %(message)s',
                    datefmt='%y-%m-%d %H:%M:%S')

import time

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
        self.gifts = {}
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
                    self.gifts[gift['id']] = gift['name']
            except Exception as e:
                logging.warning(e)

            try:
                with urllib.request.urlopen(gift_api) as f:
                    html = f.read().decode('utf-8')

                gifts_info = json.loads(html)['data']['prop_gift']
                for gift in gifts_info:
                    self.gifts[gift['id']] = gift['name']

                if self.status['room_status'] == '2':
                    self.status['room_status'] = '下播了'
                elif self.status['room_status'] == '1':
                    self.status['room_status'] = '直播中'
            except Exception as e1:
                logging.warning(e1)

            now = time.localtime()
            now_str = time.strftime('%Y-%m-%d %H:%M:%S', now)

            str_1, str_2, str_3, str_4, str_5, str_6, str_7, str_8 = self.args
            str_1.set(self.status['room_name'])
            str_2.set(self.status['owner_name'])
            str_3.set(self.status['room_status'])
            str_4.set(self.status['fans_num'])
            str_5.set(self.status['owner_weight'])
            str_6.set(self.status['online'])
            str_7.set(self.status['start_time'])
            str_8.set(now_str)

            time.sleep(60)
