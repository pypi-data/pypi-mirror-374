#!/usr/bin/env python3
"""
Schema validation example with Pydantic and dataclasses.
"""

from dataclasses import dataclass

# Try to import Pydantic (optional dependency)
try:
    from pydantic import BaseModel, Field

    PYDANTIC_AVAILABLE = True

    # Define Pydantic models
    class DatabaseConfig(BaseModel):
        host: str = "localhost"
        port: int = 5432
        name: str
        user: str
        password: str
        pool_size: int = Field(default=10, ge=1, le=100)
        timeout: int = Field(default=30, ge=1)

    class APIConfig(BaseModel):
        host: str = "0.0.0.0"
        port: int = Field(default=8000, ge=1, le=65535)
        workers: int = Field(default=4, ge=1, le=32)
        cors_origins: list[str] = []

    class AppConfig(BaseModel):
        app: dict
        database: DatabaseConfig
        api: APIConfig

except ImportError:
    PYDANTIC_AVAILABLE = False
    # Define dummy classes for when Pydantic is not available
    DatabaseConfig = None  # type: ignore
    APIConfig = None  # type: ignore
    AppConfig = None  # type: ignore

from confixer import Loader, YamlSource


# Dataclass example
@dataclass
class SimpleAppConfig:
    name: str
    version: str = "1.0.0"
    debug: bool = False
    environment: str = "production"


def pydantic_validation_example():
    """Demonstrate validation with Pydantic models."""
    if not PYDANTIC_AVAILABLE:
        print("Pydantic not available, skipping Pydantic example")
        return

    print("=== Pydantic Schema Validation ===")

    # Load config
    loader = Loader([YamlSource("config.yaml")])
    config_data = loader.load()

    try:
        # Validate with Pydantic model
        validated_config = AppConfig.model_validate(dict(config_data))

        print("Configuration is valid!")
        print(f"App: {validated_config.app}")
        print(
            f"Database: {validated_config.database.user}@{validated_config.database.host}:{validated_config.database.port}"
        )
        print(
            f"API: {validated_config.api.host}:{validated_config.api.port} ({validated_config.api.workers} workers)"
        )

    except Exception as e:
        print(f"Validation failed: {e}")


def dataclass_validation_example():
    """Demonstrate validation with dataclasses."""
    print("\n=== Dataclass Schema Validation ===")

    # Load config
    loader = Loader([YamlSource("config.yaml")])
    config_data = loader.load()

    try:
        # Extract just the app section for simple validation
        app_data = dict(config_data.app)
        validated_config = SimpleAppConfig(**app_data)

        print("Configuration is valid!")
        print(f"App: {validated_config.name} v{validated_config.version}")
        print(f"Debug: {validated_config.debug}")

    except Exception as e:
        print(f"Validation failed: {e}")


def invalid_config_example():
    """Demonstrate validation with invalid configuration."""
    print("\n=== Invalid Configuration Example ===")

    if not PYDANTIC_AVAILABLE:
        print("Pydantic not available, skipping invalid config example")
        return

    # Create invalid config data
    invalid_data = {
        "app": {"name": "TestApp"},
        "database": {
            "host": "localhost",
            "port": "not_a_number",  # Invalid port
            "name": "test",
            "user": "admin",
            "password": "secret",
        },
        "api": {
            "host": "0.0.0.0",
            "port": 99999,  # Invalid port (out of range)
            "workers": 4,
            "cors_origins": [],
        },
    }

    try:
        AppConfig.model_validate(invalid_data)
        print("Configuration is valid (unexpected!)")
    except Exception as e:
        print(f"Validation failed (expected): {e}")


if __name__ == "__main__":
    # Change to examples directory
    import os

    os.chdir(os.path.dirname(__file__))

    try:
        pydantic_validation_example()
        dataclass_validation_example()
        invalid_config_example()
    except Exception as e:
        print(f"Error: {e}")
