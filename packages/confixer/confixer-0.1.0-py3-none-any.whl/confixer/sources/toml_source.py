from .base import ConfigSource
import tomli
from typing import Any


class TomlSource(ConfigSource):
    def __init__(self, path: str):
        self.path = path

    def load(self) -> dict[str, Any]:
        with open(self.path, "rb") as f:
            data = tomli.load(f)
        if not isinstance(data, dict):
            raise ValueError(f"TOML root must be a dict, got {type(data)}")
        return data
