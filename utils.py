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

        try:
            if k not in ('txt', 'nn') and v.index('@A=') >= 0:
                items = [elem for elem in v.split('/') if len(elem) > 0]
                if len(items) == 1:
                    v = deserialize(unescape(items[0]))
                elif len(items) > 1:
                    v = [deserialize(unescape(item)) for item in items]
                # v = deserialize(v)
        except ValueError:
            pass

        result[k] = v

    return result


class UnmatchedLengthError(Exception):
    pass


class ReplyMessage:
    ERROR, WARNING, SUCCESS = range(3)

    def __init__(self, msg_type, code, data=None):
        self.type = msg_type
        self.code = code
        self.data = data


class CommandMessage:
    CONNECT, SEND, RECEIVE, CLOSE = range(4)

    def __init__(self, msg_type, data=None):
        self.type = msg_type
        self.data = data


i = 0
j = 0
room = None
stars = []
CheckVar = True
gifts = {}
cq = {
    '1': '初级酬勤',
    '2': '中级酬勤',
    '3': '高级酬勤',
}
