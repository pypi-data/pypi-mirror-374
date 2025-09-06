"""
Schema validation adapters for Pydantic and dataclasses.
"""

import importlib
from typing import Any
import dataclasses


def validate_with_schema(data: dict[str, Any], schema_ref: str) -> Any:
    """
    Validate data against a schema reference.

    Schema reference format: "module.path:ClassName"
    Example: "myapp.config:AppConfig"
    """
    try:
        module_path, class_name = schema_ref.split(":")
        module = importlib.import_module(module_path)
        schema_class = getattr(module, class_name)

        # Try Pydantic first (v2 and v1)
        if _is_pydantic_model(schema_class):
            return _validate_pydantic(data, schema_class)

        # Try dataclass
        elif dataclasses.is_dataclass(schema_class):
            return _validate_dataclass(data, schema_class)

        else:
            raise ValueError(
                f"Schema class must be a Pydantic model or dataclass, got {type(schema_class)}"
            )

    except ImportError as e:
        raise ImportError(f"Could not import schema module: {e}")
    except AttributeError as e:
        raise AttributeError(f"Schema class not found: {e}")
    except Exception as e:
        raise ValueError(f"Schema validation failed: {e}")


def _is_pydantic_model(cls: Any) -> bool:
    """Check if class is a Pydantic model (v1 or v2)."""
    try:
        # Check for Pydantic v2
        from pydantic import BaseModel as BaseModelV2

        if issubclass(cls, BaseModelV2):
            return True
    except ImportError:
        pass

    try:
        # Check for Pydantic v1
        from pydantic.v1 import BaseModel as BaseModelV1

        if issubclass(cls, BaseModelV1):
            return True
    except ImportError:
        pass

    return False


def _validate_pydantic(data: dict[str, Any], model_class: Any) -> Any:
    """Validate data using Pydantic model."""
    try:
        # Try Pydantic v2 first
        from pydantic import BaseModel as BaseModelV2

        if issubclass(model_class, BaseModelV2):
            return model_class.model_validate(data)
    except ImportError:
        pass

    try:
        # Fallback to Pydantic v1
        from pydantic.v1 import BaseModel as BaseModelV1

        if issubclass(model_class, BaseModelV1):
            return model_class.parse_obj(data)
    except ImportError:
        pass

    raise ImportError("Pydantic not available")


def _validate_dataclass(data: dict[str, Any], dataclass_type: Any) -> Any:
    """Validate data using dataclass constructor."""
    try:
        return dataclass_type(**data)
    except TypeError as e:
        raise ValueError(f"Dataclass validation failed: {e}")


class ConfigAdapter:
    """
    Adapter that wraps validated config objects with dot-notation access.
    """

    def __init__(self, validated_obj: Any):
        self._obj = validated_obj
        self._dict_cache = None

    def __getattr__(self, name: str) -> Any:
        if hasattr(self._obj, name):
            return getattr(self._obj, name)
        raise AttributeError(f"'{type(self._obj).__name__}' has no attribute '{name}'")

    def __getitem__(self, key: str) -> Any:
        if self._dict_cache is None:
            self._dict_cache = self._to_dict()
        return self._dict_cache[key]

    def _to_dict(self) -> dict[str, Any]:
        """Convert validated object to dictionary."""
        if dataclasses.is_dataclass(self._obj) and not isinstance(self._obj, type):
            return dataclasses.asdict(self._obj)

        # Try Pydantic v2
        if hasattr(self._obj, "model_dump") and callable(
            getattr(self._obj, "model_dump", None)
        ):
            return self._obj.model_dump()  # type: ignore

        # Try Pydantic v1
        if hasattr(self._obj, "dict") and callable(getattr(self._obj, "dict", None)):
            return self._obj.dict()  # type: ignore

        # Fallback
        try:
            return dict(vars(self._obj))
        except TypeError:
            # If vars() fails, return empty dict
            return {}
