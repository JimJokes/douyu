import sys

non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode+1), 0xfffd)


def escape(value):
    value = str(value)
    value = value.replace('@', '@A')
    value = value.replace('/', '@S')
    return value


def unescape(value):
    value = str(value)
    value = value.replace('@S', '/')
    value = value.replace('@A', '@')
    return value


def serialize(data):

    if data is None:
        return ''

    kv_pairs = []
    for key, value in data.items():
        kv_pairs.append(escape(key) + '@=' + escape(value))
    kv_pairs.append('')

    result = '/'.join(kv_pairs)
    return result


def deserialize(raw):

    result = {}

    if raw is None or len(raw) <= 0:
        return result

    if raw.find('/') < 0:
        return raw

    kv_pairs = raw.split('/')
    for kv_pair in kv_pairs:

        if len(kv_pair) <= 0:
            continue

        kv = kv_pair.split('@=')
        if len(kv) != 2:
            continue

        k = unescape(kv[0])
        v = unescape(kv[1])
        if not k:
            continue
        if not v:
            v = ''

        if k not in ('txt', 'nn'):
            if v.find('@A=') > 0:
                items = [elem for elem in v.split('/') if len(elem) > 0]
                # if len(items) == 1:
                #     v = deserialize(unescape(items[0]))
                # elif len(items) > 1:
                v = [deserialize(unescape(item)) for item in items]
            elif v.find('@=') > 0:
                v = deserialize(v)
            # if v.find('/') > 0:
            #     items = [elem for elem in v.split('/') if len(elem) > 0]
            #     v = [deserialize(unescape(item)) for item in items]

        result[k] = v.translate(non_bmp_map) if isinstance(v, str) else v

    return result


class UnmatchedLengthError(Exception):
    pass


class ReplyMessage:
    SUCCESS, ERROR = range(2)

    def __init__(self, style, code, data=None):
        self.style = style
        self.code = code
        self.data = data

lv = {i: 'LV%s.png' % i if i < 70 else 'LV%s.gif' % i for i in range(1, 121)}
width_cq = {i: 36+i*8 for i in range(1, 11)}
noble = {'1': 'knight.png',
         '2': 'viscount.png',
         '3': 'earl.png',
         '4': 'duke.png',
         '5': 'king.png',
         '6': 'emperor.gif',
         }
color = {
        '1': 'col_1',
        '2': 'col_2',
        '3': 'col_3',
        '4': 'col_4',
        '5': 'col_5',
        '6': 'col_6',
        }
color_cq = {
            '1': '#de744a',
            '2': '#a8bac6',
            '3': '#f1b738',
            }
bandage = {}
for i in range(1, 31):
    if i < 6:
        bandage[i] = {
            'bg': 'bandgebg_01.png',
            'md': 'bandge_01.png'
        }
    elif i < 11:
        bandage[i] = {
            'bg': 'bandgebg_02.png',
            'md': 'bandge_02.png'
        }
    elif i < 16:
        bandage[i] = {
            'bg': 'bandgebg_03.png',
            'md': 'bandge_03.png'
        }
    elif i < 21:
        bandage[i] = {
            'bg': 'bandgebg_04.png',
            'md': 'bandge_04.png'
        }
    elif i < 26:
        bandage[i] = {
            'bg': 'bandgebg_05.png',
            'md': 'bandge_05.png'
        }
    elif i < 30:
        bandage[i] = {
            'bg': 'bandgebg_06.png',
            'md': 'bandge_06.png'
        }
    else:
        bandage[i] = {
            'bg': 'bandgebg_07.png',
            'md': 'bandge_07.png'
        }
