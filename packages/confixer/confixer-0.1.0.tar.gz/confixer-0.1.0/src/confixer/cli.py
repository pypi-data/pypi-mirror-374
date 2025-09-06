"""
CLI for Confixer - configuration management tool.
"""

import json
import sys
from pathlib import Path
from typing import Optional, Any

import typer
import yaml

from .loader import Loader
from .sources.yaml_source import YamlSource
from .sources.json_source import JsonSource
from .sources.toml_source import TomlSource
from .sources.env_source import EnvSource

app = typer.Typer(help="Confixer - Modern configuration manager for Python")


@app.command()
def init(
    format: str = typer.Option("yaml", help="Config format: yaml, json, toml"),
    output: str = typer.Option("config", help="Output filename (without extension)"),
):
    """
    Initialize a new configuration file with example structure.
    """
    example_config = {
        "app": {"name": "MyApp", "version": "1.0.0", "debug": False},
        "database": {
            "host": "localhost",
            "port": 5432,
            "name": "myapp",
            "user": "admin",
        },
        "api": {"host": "0.0.0.0", "port": 8000, "workers": 4},
    }

    if format == "yaml":
        filename = f"{output}.yaml"
        with open(filename, "w", encoding="utf-8") as f:
            yaml.dump(example_config, f, default_flow_style=False, indent=2)
    elif format == "json":
        filename = f"{output}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(example_config, f, indent=2)
    elif format == "toml":
        filename = f"{output}.toml"
        try:
            import tomli_w

            with open(filename, "wb") as f:
                tomli_w.dump(example_config, f)
        except ImportError:
            typer.echo("tomli-w package required for TOML writing", err=True)
            sys.exit(1)
    else:
        typer.echo(f"Unsupported format: {format}", err=True)
        sys.exit(1)

    typer.echo(f"Created {filename}")


@app.command()
def show(
    config_path: str = typer.Argument(help="Path to configuration file"),
    env_file: Optional[str] = typer.Option(None, "--env", help="Path to .env file"),
    prefix: Optional[str] = typer.Option(
        None, "--prefix", help="Environment variable prefix"
    ),
    path: Optional[str] = typer.Option(
        None, "--path", help="Dot-separated path to show (e.g., 'app.name')"
    ),
    set_values: Optional[list[str]] = typer.Option(
        None, "--set", help="Override values (key=value)"
    ),
    format: str = typer.Option("json", help="Output format: json, yaml"),
):
    """
    Load and display merged configuration.
    """
    try:
        # Determine source type from file extension
        config_path_obj = Path(config_path)
        if not config_path_obj.exists():
            typer.echo(f"Config file not found: {config_path}", err=True)
            sys.exit(1)

        sources = []

        # Add config file source
        extension = config_path_obj.suffix.lower()
        if extension == ".yaml" or extension == ".yml":
            sources.append(YamlSource(config_path))
        elif extension == ".json":
            sources.append(JsonSource(config_path))
        elif extension == ".toml":
            sources.append(TomlSource(config_path))
        else:
            typer.echo(f"Unsupported config format: {extension}", err=True)
            sys.exit(1)

        # Add environment source
        sources.append(EnvSource(path=env_file, prefix=prefix))

        # Load configuration
        loader = Loader(sources)
        config = loader.load()

        # Apply runtime overrides
        if set_values:
            for override in set_values:
                if "=" not in override:
                    typer.echo(
                        f"Invalid override format: {override} (expected key=value)",
                        err=True,
                    )
                    sys.exit(1)
                key, value = override.split("=", 1)
                _set_nested_value(config, key, value)

        # Get specific path if requested
        result = config
        if path:
            result = _get_nested_value(config, path)

        # Output result
        if format == "json":
            typer.echo(json.dumps(result, indent=2))
        elif format == "yaml":
            typer.echo(yaml.dump(result, default_flow_style=False, indent=2))
        else:
            typer.echo(f"Unsupported output format: {format}", err=True)
            sys.exit(1)

    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        sys.exit(1)


@app.command()
def validate(
    config_path: str = typer.Argument(help="Path to configuration file"),
    schema: Optional[str] = typer.Option(
        None, "--schema", help="Schema module:class (e.g., 'myapp.config:AppConfig')"
    ),
):
    """
    Validate configuration against a schema.
    """
    try:
        config_path_obj = Path(config_path)
        if not config_path_obj.exists():
            typer.echo(f"Config file not found: {config_path}", err=True)
            sys.exit(1)

        # Load config
        extension = config_path_obj.suffix.lower()
        filename = config_path_obj.name

        if extension == ".yaml" or extension == ".yml":
            source = YamlSource(config_path)
        elif extension == ".json":
            source = JsonSource(config_path)
        elif extension == ".toml":
            source = TomlSource(config_path)
        elif filename == ".env" or filename.endswith(".env"):
            source = EnvSource(path=config_path)
        else:
            typer.echo(
                f"Unsupported config format: {extension} (file: {filename})", err=True
            )
            sys.exit(1)

        config_data = source.load()

        if schema:
            # Import and validate with schema
            from .schema import validate_with_schema

            validate_with_schema(config_data, schema)
            typer.echo("Configuration is valid")
        else:
            # Just check if config loads correctly
            typer.echo("Configuration syntax is valid")

    except Exception as e:
        typer.echo(f"Validation failed: {e}", err=True)
        sys.exit(1)


def _get_nested_value(obj: dict[str, Any], path: str) -> Any:
    """Get nested value using dot notation."""
    parts = path.split(".")
    current = obj
    for part in parts:
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            raise KeyError(f"Path not found: {path}")
    return current


def _set_nested_value(obj: dict[str, Any], path: str, value: str) -> None:
    """Set nested value using dot notation."""
    parts = path.split(".")
    current = obj

    # Navigate to parent
    for part in parts[:-1]:
        if part not in current:
            current[part] = {}
        current = current[part]

    # Set final value with type coercion
    final_key = parts[-1]
    current[final_key] = _coerce_cli_value(value)


def _coerce_cli_value(value: str) -> Any:
    """Coerce CLI string value to appropriate Python type."""
    # Handle boolean values
    if value.lower() in ("true", "yes", "1", "on"):
        return True
    if value.lower() in ("false", "no", "0", "off"):
        return False

    # Handle numeric values
    try:
        if "." not in value:
            return int(value)
        return float(value)
    except ValueError:
        pass

    # Handle null/none values
    if value.lower() in ("null", "none", "nil"):
        return None

    return value


if __name__ == "__main__":
    app()
