from abc import ABC, abstractmethod
from typing import Any


class ConfigSource(ABC):
    """
    Abstract base class for a configuration source.
    all sources (YAML, JSON, TOML, .env) must implement load().
    """

    @abstractmethod
    def load(self) -> dict[str, Any]:
        """
        Load configuration and return as dictionary.
        """
        pass
