from .base import ConfigSource
import json
from typing import Any


class JsonSource(ConfigSource):
    def __init__(self, path: str):
        self.path = path

    def load(self) -> dict[str, Any]:
        with open(self.path, encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            raise ValueError(f"JSON root must be a dict, got {type(data)}")
        return data
