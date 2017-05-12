import time, threading

from chat.room import ChatRoom


def write(_message):
    with open(r'D:\workspace\douyu.txt', 'a') as f:
        f.write(_message + '\n')


def gift_num(msg):
    global yuwan, zan, ruoji, liu, feiji, huojian, cq1, cq2, cq3

    giftid = msg.attr('gfid')
    lev = msg.attr('lev')
    # try:
    if giftid == '506':
        yuwan += 1
    elif giftid == '507':
        zan += 1
    elif giftid == '508':
        ruoji += 1
    elif giftid == '509':
        liu += 1
    elif giftid == '510':
        feiji += 1
    elif giftid == "511":
        huojian += 1
    if lev == '1':
        cq1 += 1
    elif lev == '2':
        cq2 += 1
    elif lev == '3':
        cq3 += 1
    '''except:
        pass'''


def num(_time, _roomid):

    while True:
        time.sleep(_time)
        print(time.strftime("%y-%m-%d %H:%M:%S", time.localtime())+':\n' +
              '[%s]冰淇淋球总共%d个' % (rooms[_roomid], yuwan) + '\n' +
              '[%s]圣诞赞一个总共%d个' % (rooms[_roomid], zan) + '\n' +
              '[%s]小雪人总共%d个' % (rooms[_roomid], ruoji) + '\n' +
              '[%s]姜饼屋总共%d个' % (rooms[_roomid], liu) + '\n' +
              '[%s]圣诞飞机总共%d个' % (rooms[_roomid], feiji) + '\n' +
              '[%s]圣诞火箭总共%d个' % (rooms[_roomid], huojian)+'\n' +
              '[%s]初级酬勤总共%d个' % (rooms[_roomid], cq1)+'\n' +
              '[%s]中级酬勤总共%d个' % (rooms[_roomid], cq2) + '\n' +
              '[%s]高级酬勤总共%d个' % (rooms[_roomid], cq3))


def chat_message(msg):
    now = time.strftime("%y-%m-%d %H:%M:%S", time.localtime())
    _roomid = msg.attr('rid')
    _uname = msg.attr('nn')
    _ct = msg.attr('ct')
    if _ct is None:
        _ct = '网页'
    else:
        _ct = '手机'
    if _uname == '小缘' or _uname == '芒果唇膏' or _uname == '麻辣烫超好吃':
        if msg.attr('type') == 'chatmsg':
            message = '%s [%s]:[%s][%s][等级:%s]:%s' % (now, rooms[_roomid], _ct, _uname, msg.attr('level'), msg.attr('txt'))
            print(message)
            write(message)
        else:
            message = '%s [%s]:[%s][等级:%s] 进入了直播间!' % (now, rooms[_roomid], _uname, msg.attr('level'))
            print('\033[33m' + message + '\033[0m')
            write(message)


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
        message = '\033[33m' + '%s [%s]:[%s][等级:%s] 进入了直播间!' % (now, rooms[_roomid], _uname, msg.attr('level')) + '\033[0m'
    print(message)


# 计算礼物数量
def gift(_roomid, _time=30):

    app = threading.Thread(target=num, args=(_time, _roomid))
    app.setDaemon = True
    app.start()
    _room = ChatRoom(_roomid)
    _room.on('dgb', gift_num)
    _room.on('bc_buy_deserve', gift_num)
    print('开始计算[%s]的直播间礼物数量！' % rooms[_roomid])
    _room.knock()


# 获取所有弹幕
def alldanmu(_roomid):
    _room = ChatRoom(_roomid)
    _room.on('chatmsg', on_chat_message)
    _room.on('uenter', on_chat_message)
    # print('开始监控[%s]的直播间弹幕！' % rooms[_roomid])
    _room.knock()


# 捕捉小缘
def catch_yukari(_roomid):
    _room = ChatRoom(_roomid)
    _room.on('chatmsg', chat_message)
    _room.on('uenter', chat_message)
    print('开始在[%s]的直播间捕捉小缘！' % rooms[_roomid])
    _room.knock()

if __name__ == '__main__':
    global rooms
    rooms = {
        '196': '小缘',
        '160141': '小白脸',
        '229346': '钱佳',
        '283566': '皮皮虾',
        '60937': '炸得',
        '13703': '火焰鼠',
        '22': '时光机'
    }
    yuwan = 0
    zan = 0
    ruoji = 0
    liu = 0
    feiji = 0
    huojian = 0
    cq1 = 0
    cq2 = 0
    cq3 = 0
    print('请选择工作内容：1、监控弹幕，2、捕捉小缘，3、计算礼物数量')
    _id = input()
    print('请输入直播间号：')
    for k, v in rooms.items():
        print('%s : %s' % (k, v))
    _roomid = input()
    if _id == '1':
        # 获取所有弹幕
        alldanmu(_roomid)
    elif _id == '2':
        # 捕捉小缘
        catch_yukari(_roomid)
    elif _id == '3':
        # 计算礼物数量
        gift(_roomid, 30)
