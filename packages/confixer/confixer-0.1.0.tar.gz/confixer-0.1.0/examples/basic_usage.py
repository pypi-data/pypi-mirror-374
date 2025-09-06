#!/usr/bin/env python3
"""
Basic usage example for Confixer.
"""

from confixer import Loader, YamlSource, EnvSource


def basic_example():
    """Load configuration from YAML file and environment variables."""
    print("=== Basic Configuration Loading ===")

    # Create loader with YAML file and environment variables
    loader = Loader(
        [
            YamlSource("config.yaml"),
            EnvSource(prefix="APP_"),  # Only load APP_* environment variables
        ]
    )

    # Load merged configuration
    config = loader.load()

    # Access using dot notation
    print(f"App name: {config.app.name}")
    print(f"Database host: {config.database.host}")
    print(f"API port: {config.api.port}")

    # Access using dictionary notation
    print(f"Debug mode: {config['app']['debug']}")

    # Print entire config
    print("\nComplete configuration:")
    import json

    print(json.dumps(dict(config), indent=2))


def env_nesting_example():
    """Demonstrate environment variable nesting with __ separator."""
    print("\n=== Environment Variable Nesting ===")

    # Load from .env file with nesting
    loader = Loader([EnvSource(path=".env")])

    config = loader.load()

    # Show nested structure from environment variables
    if "DB" in config:
        print(f"DB Host: {config.DB.HOST}")
        print(f"DB Port: {config.DB.PORT}")
        print(f"DB Pool Size: {config.DB.POOL_SIZE}")

    if "API" in config:
        print(f"API Host: {config.API.HOST}")
        print(f"API Debug: {config.API.DEBUG}")


def layered_override_example():
    """Demonstrate layered configuration overrides."""
    print("\n=== Layered Configuration Overrides ===")

    # Create loader with multiple layers (base → env overrides)
    loader = Loader(
        [
            YamlSource("config.yaml"),  # Base configuration
            EnvSource(path=".env"),  # Environment overrides
        ]
    )

    config = loader.load()

    # Show how environment variables override base config
    print("Database host (base): localhost")
    print(f"Database host (final): {config.database.host}")
    print("API port (base): 8000")
    print(f"API port (final): {config.api.port}")
    print(f"Debug mode (final): {config.app.debug}")


if __name__ == "__main__":
    # Change to examples directory
    import os

    os.chdir(os.path.dirname(__file__))

    try:
        basic_example()
        env_nesting_example()
        layered_override_example()
    except Exception as e:
        print(f"Error: {e}")
