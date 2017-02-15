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
            if k == 'nl' or k == 'list_level':
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
