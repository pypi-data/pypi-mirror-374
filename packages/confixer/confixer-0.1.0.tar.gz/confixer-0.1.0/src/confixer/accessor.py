class DotConfig(dict):
    """
    A dict subclass that allows attribute-style access (dot notation).
    Example:
        cfg = DotConfig({"db": {"host": "localhost"}})
        print(cfg.db.host) # localhost
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # wrap nested dicts
        for key, value in self.items():
            if isinstance(value, dict):
                self[key] = DotConfig(value)

    def __getattr__(self, item):
        try:
            return self[item]
        except KeyError:
            raise AttributeError(item)

    def __setattr__(self, key, value):
        if isinstance(value, dict):
            value = DotConfig(value)
        self[key] = value

    def __delattr__(self, key):
        try:
            del self[key]
        except KeyError:
            raise AttributeError(key)
