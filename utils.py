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

        # try:
        #     if v.index('@=') >= 0:
        #         v = deserialize(v)
        # except ValueError as e:
        #     pass
        try:
            if k in ('nl', 'list_level', 'frank'):
                v = deserialize2(unescape(v))
        except ValueError:
            pass

        result[k] = v

    return result


def deserialize2(raw):

    result = {}

    if raw is None or len(raw) <= 0:
        return result

    i = 1
    buffs = raw.split('//')
    for buff in buffs:

        if len(buff) <= 0:
            continue

        user = {}
        kv_pairs = buff.split('/')
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

            user[k] = v

        if not user:
            continue

        result[i] = user
        i += 1

    return result

widths = [
    (126,   1), (159,   0), (687,   1), (710,   0), (711,   1),
    (727,   0), (733,   1), (879,   0), (1154,  1), (1161,  0),
    (4347,  1), (4447,  2), (7467,  1), (7521,  0), (8369,  1),
    (8426,  0), (9000,  1), (9002,  2), (11021, 1), (12350, 2),
    (12351, 1), (12438, 2), (12442, 0), (19893, 2), (19967, 1),
    (55203, 2), (63743, 1), (64106, 2), (65039, 1), (65059, 0),
    (65131, 2), (65279, 1), (65376, 2), (65500, 1), (65510, 2),
    (120831, 1), (262141, 2), (1114109, 1),
]


def get_width(o):
    """Return the screen column width for unicode ordinal o."""
    # global widths
    if o == 0xe or o == 0xf:
        return 0
    for num, wid in widths:
        if o <= num:
            return wid
    return 1


def align_right(text, width):
    count = 0
    for char in text:
        code = ord(char)
        if get_width(code) == 2:
            count += 2
        elif get_width(code) == 1:
            count += 1
        else:
            continue
    return text + ' ' * (width - count)


i = 0
j = 0
room = None
stars = []
CheckVar = True
