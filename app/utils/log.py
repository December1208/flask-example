def gen_log_prefix(tag, clue=None):
    prefix = '[{}]'.format(tag.upper())
    if clue:
        prefix = '{}[{}]'.format(prefix, clue)
    return prefix
