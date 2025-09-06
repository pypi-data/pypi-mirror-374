# Confixer 🔧

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A modern configuration manager for Python that unifies multi-source configs (YAML, JSON, TOML, .env, environment variables, CLI args, runtime overrides) into a single validated, dot-accessible object.

## ✨ Features

- **🔄 Multi-format loading** - YAML, JSON, TOML, .env files, and environment variables
- **📚 Layered overrides** - `base config → env vars → CLI args → runtime` with deep merge
- **🎯 Dot-notation access** - `config.database.host` instead of `config["database"]["host"]`
- **✅ Schema validation** - Pydantic models and dataclasses support
- **🛠️ CLI tool** - Initialize, show, and validate configurations
- **🪢 Environment nesting** - `DB__HOST=localhost` becomes `{"DB": {"HOST": "localhost"}}`
- **🔒 Type coercion** - Automatic conversion of strings to bool/int/float/None

## 🚀 Quick Start

### Installation

```bash
pip install confixer
```

### Basic Usage

```python
from confixer import Loader, YamlSource, EnvSource

# Create loader with multiple sources (layered overrides)
loader = Loader([
    YamlSource("config.yaml"),      # Base configuration
    EnvSource(prefix="APP_")        # Environment overrides
])

# Load and merge all sources
config = loader.load()

# Access with dot notation
print(config.database.host)        # "localhost"
print(config.api.port)             # 8080

# Still works like a dictionary
print(config["database"]["host"])   # "localhost"
```

## 📖 Full Documentation

### Configuration Sources

#### YAML Source
```python
from confixer import YamlSource

source = YamlSource("config.yaml")
data = source.load()
```

#### JSON Source
```python
from confixer import JsonSource

source = JsonSource("config.json")
data = source.load()
```

#### TOML Source
```python
from confixer import TomlSource

source = TomlSource("config.toml")
data = source.load()
```

#### Environment Source
```python
from confixer import EnvSource

# Load from environment variables
env_source = EnvSource()

# Load from .env file
env_source = EnvSource(path=".env")

# Filter by prefix (APP_DEBUG → DEBUG)
env_source = EnvSource(prefix="APP_")

# Nested environment variables
# DB__HOST=localhost → {"DB": {"HOST": "localhost"}}
# DB__PORT=5432 → {"DB": {"PORT": 5432}}
```

### Layered Configuration

```python
from confixer import Loader, YamlSource, EnvSource

# Sources are merged in order: base → overrides
loader = Loader([
    YamlSource("config.yaml"),          # Base config
    YamlSource("config.local.yaml"),    # Local overrides  
    EnvSource(path=".env"),             # Environment file
    EnvSource(prefix="APP_"),           # Environment variables
])

config = loader.load()
```

### Environment Variable Nesting & Type Coercion

```bash
# Environment variables
export DB__HOST=localhost
export DB__PORT=5432
export DB__ENABLED=true
export DB__TIMEOUT=30.5
export DB__PASSWORD=secret123
```

```python
from confixer import EnvSource

source = EnvSource()
config = source.load()

print(config.DB.HOST)      # "localhost" (string)
print(config.DB.PORT)      # 5432 (int)
print(config.DB.ENABLED)   # True (bool)
print(config.DB.TIMEOUT)   # 30.5 (float)
print(config.DB.PASSWORD)  # "secret123" (string)
```

**Type Coercion Rules:**
- **Booleans**: `true`, `yes`, `1`, `on` → `True` | `false`, `no`, `0`, `off` → `False`
- **Numbers**: `123` → `123` (int) | `123.45` → `123.45` (float)
- **None**: `null`, `none`, `nil` → `None`
- **Strings**: Everything else remains as string

### Schema Validation

#### With Pydantic
```python
from pydantic import BaseModel
from confixer import Loader, YamlSource, validate_with_schema

class DatabaseConfig(BaseModel):
    host: str = "localhost"
    port: int = 5432
    name: str
    user: str
    
class AppConfig(BaseModel):
    debug: bool = False
    database: DatabaseConfig

# Load and validate
loader = Loader([YamlSource("config.yaml")])
config_data = loader.load()

# Validate with schema
validated = validate_with_schema(dict(config_data), "myapp.models:AppConfig")
print(validated.database.host)
```

#### With Dataclasses
```python
from dataclasses import dataclass
from confixer import validate_with_schema

@dataclass
class AppConfig:
    name: str
    debug: bool = False
    port: int = 8000

# Validate
config_data = {"name": "MyApp", "debug": True}
validated = validate_with_schema(config_data, "__main__:AppConfig")
```

## 🛠️ CLI Tool

The `confixer` CLI provides commands to initialize, show, and validate configurations.

### Initialize Configuration
```bash
# Create example YAML config
confixer init --format yaml --output config

# Create JSON config  
confixer init --format json --output settings

# Create TOML config
confixer init --format toml --output app
```

### Show Merged Configuration
```bash
# Show merged config from YAML + environment
confixer show config.yaml

# With .env file
confixer show config.yaml --env .env

# With environment variable prefix
confixer show config.yaml --prefix APP_

# Show specific nested path
confixer show config.yaml --path database.host

# Runtime overrides
confixer show config.yaml --set database.port=5433 --set app.debug=true

# Output as YAML
confixer show config.yaml --format yaml
```

### Validate Configuration
```bash
# Basic syntax validation
confixer validate config.yaml

# Schema validation
confixer validate config.yaml --schema myapp.config:AppConfig
```

## 📁 Example Files

### config.yaml
```yaml
app:
  name: "MyApp"
  version: "1.0.0"
  debug: false

database:
  host: "localhost"
  port: 5432
  name: "myapp"
  user: "admin"

api:
  host: "0.0.0.0"
  port: 8000
  workers: 4
```

### .env
```bash
# Override database settings
DB__HOST=prod-db.example.com
DB__PORT=5432
DB__PASSWORD=secret123

# Override API settings
API__HOST=0.0.0.0
API__PORT=8080
API__DEBUG=true

# App settings
APP__ENVIRONMENT=production
APP__LOG_LEVEL=INFO
```

### Usage Example
```python
from confixer import Loader, YamlSource, EnvSource

# Load with environment overrides
loader = Loader([
    YamlSource("config.yaml"),      # Base: DB host = localhost
    EnvSource(path=".env")          # Override: DB host = prod-db.example.com
])

config = loader.load()

print(config.database.host)  # "prod-db.example.com" (from .env)
print(config.database.port)  # 5432 (from .env, coerced to int)
print(config.api.debug)      # True (from .env, coerced to bool)
print(config.app.name)       # "MyApp" (from YAML, not overridden)
```

## 🏗️ Architecture

```
confixer/
├─ merge.py         # deep_merge() for layered configs
├─ accessor.py      # DotConfig class (dot notation)  
├─ loader.py        # Main Loader class
├─ schema.py        # Validation (Pydantic/dataclasses)
├─ cli.py          # CLI commands (Typer)
└─ sources/
   ├─ base.py       # ConfigSource interface
   ├─ yaml_source.py
   ├─ json_source.py  
   ├─ toml_source.py
   └─ env_source.py  # Environment + .env + nesting
```

## 🔄 Configuration Flow

1. **Load** - Each source loads its data into a dict
2. **Merge** - Deep merge all sources in order (later overrides earlier)
3. **Wrap** - Wrap result in `DotConfig` for dot-notation access
4. **Validate** - Optional schema validation with Pydantic/dataclasses
5. **Access** - Use `config.key.subkey` or `config["key"]["subkey"]`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make changes and add tests
4. Run tests: `pytest`
5. Run pre-commit: `pre-commit run --all-files`
6. Commit changes: `git commit -m 'Add amazing feature'`
7. Push to branch: `git push origin feature/amazing-feature`
8. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Typer](https://typer.tiangolo.com/) for the CLI
- [Pydantic](https://pydantic-docs.helpmanual.io/) for validation
- [PyYAML](https://pyyaml.org/), [tomli](https://github.com/hukkin/tomli), [python-dotenv](https://github.com/theskumar/python-dotenv) for format support

---

**Confixer** - Making configuration management simple, layered, and type-safe! 🔧
