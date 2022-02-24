def valid_values_of_enum_class(enum_class):
    invalid_keys = list(filter(lambda x: not x.startswith('__'), enum_class.__dict__.keys()))
    return set([getattr(enum_class, key) for key in invalid_keys])
