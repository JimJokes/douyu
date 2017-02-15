from chat.room import ChatRoom
from chat.network.utils import *
from chat.network.client import Client
import time, threading


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


def test():
    b = b'type@=online_noble_list/num@=20/nl@=uid@AA=611483@ASnn@AA=\xe5\xb0\x8f\xe7\xbc\x98\xe8\xb5\x90\xe5\x90\x8d\xe7\x9a\x84\xe5\xb0\x8f\xe5\x85\xb3@ASicon@AA=avanew@AASface@AAS201612@AAS10@AAS16@AAS78eb846756b47bb10ba497d16c9c34d1@ASne@AA=1@ASlv@AA=36@ASpg@AA=1@ASrg@AA=4@AS@Suid@AA=51126709@ASnn@AA=\xe9\xa9\xac\xe7\x8c\xb4\xe7\x83\xa7\xe9\x85\x92\xe5\xb0\x8f\xe7\xbc\x98@ASicon@AA=avanew@AASface@AAS201612@AAS27@AAS21@AAS7bcdc0700e8a7a09f1bf888620cb0e73@ASne@AA=1@ASlv@AA=32@ASpg@AA=1@ASrg@AA=4@AS@Suid@AA=571935@ASnn@AA=Snape196@ASicon@AA=avanew@AASface@AAS201701@AAS19@AAS16@AAS621035ae663cca9ea1d2bf2795c1bd92@ASne@AA=1@ASlv@AA=27@ASpg@AA=1@ASrg@AA=1@AS@Suid@AA=5156507@ASnn@AA=\xe9\xa3\x8e\xe6\x97\xa0\xe5\xbf\xa7@ASicon@AA=avanew@AASface@AAS201612@AAS30@AAS17@AAS04bf9542b5e875731fa53b579ee36ab1@ASne@AA=1@ASlv@AA=25@ASpg@AA=1@ASrg@AA=1@AS@Suid@AA=79932847@ASnn@AA=\xe5\xb0\x8f\xe7\xbc\x98\xe7\x9a\x8436D@ASicon@AA=avanew@AASface@AAS201612@AAS26@AAS04@AASc2daca2c31aacda92a3abeb0fa39642e@ASne@AA=1@ASlv@AA=23@ASpg@AA=1@ASrg@AA=1@AS@Suid@AA=209251@ASnn@AA=\xe6\x88\x91\xe6\x98\xaf\xe7\x9b\xb4\xe7\x9a\x84@ASicon@AA=avanew@AASface@AAS201612@AAS24@AAS23@AASbfc177ec6ada76b0a4986e88b9e9d551@ASne@AA=1@ASlv@AA=22@ASpg@AA=1@ASrg@AA=1@AS@Suid@AA=61264573@ASnn@AA=\xe9\xbb\xaf\xe8\x89\xb2\xe5\x91\xa8\xe6\x9c\xab@ASicon@AA=avanew@AASface@AAS201612@AAS25@AAS02@AAScf03e5d76826ea99caa1d8d47a84b7dd@ASne@AA=1@ASlv@AA=21@ASpg@AA=1@ASrg@AA=1@AS@Suid@AA=2219947@ASnn@AA=\xe5\xb0\x8f\xe7\xbc\x98\xe5\x96\xb5\xe7\x9a\x84\xe9\xad\x94\xe6\xb3\x95\xe8\xa3\x9d\xe5\x82\x99@ASicon@AA=avanew@AASface@AAS201701@AAS09@AAS00@AAS0c155d24da948b8b609cc24e28f7dbc5@ASne@AA=1@ASlv@AA=21@ASpg@AA=1@ASrg@AA=1@AS@Suid@AA=5357843@ASnn@AA=\xe9\xa9\xbe\xe9\xa9\xb6\xe7\xbc\x98\xe6\xb5\x85\xe5\xb2\x9b@ASicon@AA=avanew@AASface@AAS201702@AAS07@AAS08@AASdd18912bd1c3f840db3c2ed11b3cd5b0@ASne@AA=1@ASlv@AA=20@ASpg@AA=1@ASrg@AA=1@AS@Suid@AA=17439814@ASnn@AA=\xe5\xbc\x8bDrlv@ASicon@AA=avanew@AASface@AAS201701@AAS24@AAS01@AAS561bf7e5c9dd93e31f33b750e80ca1f8@ASne@AA=1@ASlv@AA=20@ASpg@AA=1@ASrg@AA=1@AS@Suid@AA=14639036@ASnn@AA=jun190@ASicon@AA=avanew@AASface@AAS201612@AAS25@AAS00@AAS4f29be145dfb0c5caf7ce3901dc42346@ASne@AA=1@ASlv@AA=20@ASpg@AA=1@ASrg@AA=1@AS@Suid@AA=47449605@ASnn@AA=D\xe5\xbc\xa0\xe8\x91\xa3\xe7\x9a\x84\xe7\x9c\xb7\xe6\x81\x8b@ASicon@AA=avanew@AASface@AAS201612@AAS30@AAS19@AASec6348ca3aa15a5ff490350ccbed9b19@ASne@AA=1@ASlv@AA=20@ASpg@AA=1@ASrg@AA=1@AS@Suid@AA=44286036@ASnn@AA=\xe6\x9c\xba\xe5\xb7\xa7\xe5\xb0\x8f\xe7\xbc\x98\xe4\xb8\x8d\xe5\x92\xac\xe8\x88\x8c@ASicon@AA=avatar@AASface@AAS201605@AAS28@AAS4a6e18192b23ff0560b827698b591cd9@ASne@AA=1@ASlv@AA=19@ASpg@AA=1@ASrg@AA=1@AS@Suid@AA=61386910@ASnn@AA=\xe5\xb0\x8f\xe7\xbc\x98\xe4\xb8\x93\xe5\xb1\x9e\xe5\xa5\xb3\xe4\xbb\x86\xe6\x9f\xbf\xe5\xad\x90@ASicon@AA=avanew@AASface@AAS201610@AAS26@AAS22@AASa665dd0f487d7c506425d440fcfe2cda@ASne@AA=1@ASlv@AA=19@ASpg@AA=1@ASrg@AA=1@AS@Suid@AA=1037228@ASnn@AA=\xe8\xb5\xa4\xe7\x9e\xb3\xe4\xb8\x8d\xe6\x98\xaf\xe7\xbf\x85\xe6\xa1\xb6\xe6\x98\xaf\xe8\xb5\xa4\xe7\x9e\xb3@ASicon@AA=avatar@AASface@AAS201603@AAS869494616e039c0a08e884a976d282d5@ASne@AA=1@ASlv@AA=18@ASpg@AA=1@ASrg@AA=4@AS@Suid@AA=9124720@ASnn@AA=\xe5\xa5\xbd\xe6\x83\xb3\xe5\x90\x83\xe9\xba\xbb\xe8\xbe\xa3\xe9\xa6\x99\xe9\x94\x85@ASicon@AA=avanew@AASface@AAS201702@AAS07@AAS12@AAS6183861792df196e247b3b7380e7062c@ASne@AA=1@ASlv@AA=18@ASpg@AA=1@ASrg@AA=1@AS@Suid@AA=88464668@ASnn@AA=\xe7\xad\x89\xe4\xb8\x80\xe4\xb8\xaa\xe7\xbc\x98\xe5\xbf\x83@ASicon@AA=avanew@AASface@AAS201701@AAS01@AAS10@AASecd50a98fda74385a587b7cd1ce9f4fe@ASne@AA=1@ASlv@AA=17@ASpg@AA=1@ASrg@AA=1@AS@Suid@AA=71374661@ASnn@AA=sherry22422@ASicon@AA=avanew@AASface@AAS201609@AAS28@AAS23@AAS785a9419e50d87dac2fa65c2caa6684c@ASne@AA=1@ASlv@AA=17@ASpg@AA=1@ASrg@AA=1@AS@Suid@AA=60196855@ASnn@AA=\xe9\x91\xab\xe5\xae\x87you@ASicon@AA=avatar@AASface@AAS201607@AAS24@AAS7f2660195efba164645bc78a0ceeb2dc@ASne@AA=1@ASlv@AA=16@ASpg@AA=1@ASrg@AA=1@AS@Suid@AA=105294891@ASnn@AA=\xe6\xaf\x81\xe7\x81\xad\xe7\xae\xad@ASicon@AA=avanew@AASface@AAS201701@AAS22@AAS18@AAS0b5c54cce1a328e8f9d38352d5715ca1@ASne@AA=1@ASlv@AA=13@ASpg@AA=1@ASrg@AA=1@AS@S/rid@=196/\x00'
    # b = b'nn@AA=\xe8\xb5\xa4\xe7\x9e\xb3\xe4\xb8\x8d\xe6\x98\xaf\xe7\xbf\x85\xe6\xa1\xb6\xe6\x98\xaf\xe8\xb5\xa4\xe7\x9e\xb3@ASic'
    # try:
    #     b = b.decode('utf-8')
    #     print(b)
    # except UnicodeDecodeError as e:
    #     print(e)
    b = b.decode()
    b = deserialize(b)
    # b = unescape(b)
    # b = unescape(b)
    # b = unescape(b)
    # b = unescape(b)
    # b = unescape(b)

    print(b)



if __name__ == '__main__':
    start()
    # test()
