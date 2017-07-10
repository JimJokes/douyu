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
                if len(items) == 1:
                    v = deserialize(unescape(items[0]))
                elif len(items) > 1:
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


class CommandMessage:
    CONNECT, SEND, RECEIVE, CLOSE = range(4)

    def __init__(self, msg_type, data=None):
        self.type = msg_type
        self.data = data
