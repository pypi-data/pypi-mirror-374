def deep_merge(a: dict, b: dict) -> dict:
    """
    Deep merge 2 dictionaries.

    Values from b override values from a.
    Nested dicts are merged recursively.
    Lists and primitives are replaced.
    """
    result = dict(a)
    for key, value in b.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result
