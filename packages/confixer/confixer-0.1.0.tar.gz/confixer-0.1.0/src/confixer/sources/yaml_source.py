from .base import ConfigSource
import yaml
from typing import Any


class YamlSource(ConfigSource):
    def __init__(self, path: str):
        self.path = path

    def load(self) -> dict[str, Any]:
        # load yaml file and return dict
        with open(self.path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if not isinstance(data, dict):
            raise ValueError(f"YAML root must be a dict, got {type(data)}")
        return data
