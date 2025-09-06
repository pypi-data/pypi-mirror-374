from .merge import deep_merge
from .accessor import DotConfig
from .sources.base import ConfigSource


class Loader:
    def __init__(self, layers: list[ConfigSource]):
        self.layers = layers

    def load(self) -> DotConfig:
        result = {}
        for layer in self.layers:
            data = layer.load()
            result = deep_merge(result, data)
        return DotConfig(result)
