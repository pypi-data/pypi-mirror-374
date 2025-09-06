"""
Confixer - Modern configuration manager for Python.

Load YAML/JSON/TOML/.env, apply layered overrides, validate with schemas.
"""

from .loader import Loader
from .accessor import DotConfig
from .merge import deep_merge
from .schema import validate_with_schema, ConfigAdapter

from .sources.base import ConfigSource
from .sources.yaml_source import YamlSource
from .sources.json_source import JsonSource
from .sources.toml_source import TomlSource
from .sources.env_source import EnvSource

__version__ = "0.1.0"
__all__ = [
    "Loader",
    "DotConfig",
    "deep_merge",
    "validate_with_schema",
    "ConfigAdapter",
    "ConfigSource",
    "YamlSource",
    "JsonSource",
    "TomlSource",
    "EnvSource",
]
