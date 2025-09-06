from .base import ConfigSource
import os
from dotenv import dotenv_values
from typing import Any, Optional


class EnvSource(ConfigSource):
    def __init__(self, path: Optional[str] = None, prefix: Optional[str] = None):
        self.path = path
        self.prefix = prefix

    def load(self) -> dict[str, Any]:
        data: dict[str, str] = dict(os.environ)

        if self.path:
            dotenv_data = dotenv_values(self.path)
            # Drop None values
            cleaned = {k: v for k, v in dotenv_data.items() if v not in (None, "")}

            data.update(cleaned)

        if self.prefix:
            data = {
                k[len(self.prefix) :]: v
                for k, v in data.items()
                if k.startswith(self.prefix)
            }

        return self._nest_keys(data)

    def _nest_keys(self, flat: dict[str, str]) -> dict[str, Any]:
        """
        Convert flat keys with __ separators to nested dicts.
        Example: DB__HOST=localhost -> {"DB": {"HOST": "localhost"}}
        """
        result: dict[str, Any] = {}

        for key, value in flat.items():
            # Split on __ to create nested structure
            parts = key.split("__")
            current = result

            # Navigate/create nested structure
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]

            # Set final value with type coercion
            final_key = parts[-1]
            current[final_key] = self._coerce_value(value)

        return result

    def _coerce_value(self, value: str) -> Any:
        """
        Coerce string values to appropriate Python types.
        """
        # Handle boolean values
        if value.lower() in ("true", "yes", "1", "on"):
            return True
        if value.lower() in ("false", "no", "0", "off"):
            return False

        # Handle numeric values
        try:
            # Try integer first
            if "." not in value:
                return int(value)
            # Try float
            return float(value)
        except ValueError:
            pass

        # Handle null/none values
        if value.lower() in ("null", "none", "nil"):
            return None

        # Return as string if no coercion applies
        return value
