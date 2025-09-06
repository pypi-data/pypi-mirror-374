# Confixer CLI Examples

This file demonstrates how to use the Confixer CLI tool.

## Installation & Setup

First, make sure Confixer is installed and the CLI is available:

```bash
pip install confixer
# or for development
pip install -e .
```

## Initialize Configuration

Create example configuration files:

```bash
# Create YAML config
confixer init --format yaml --output myapp
# Creates myapp.yaml

# Create JSON config  
confixer init --format json --output config
# Creates config.json

# Create TOML config
confixer init --format toml --output settings
# Creates settings.toml
```

## Show Configuration

Display merged configuration from multiple sources:

```bash
# Show config from YAML file
confixer show config.yaml

# Show config with environment variables (with prefix)
confixer show config.yaml --prefix APP_

# Show config with .env file
confixer show config.yaml --env .env

# Show specific configuration path
confixer show config.yaml --path database.host

# Show with runtime overrides
confixer show config.yaml --set database.port=5433 --set app.debug=true

# Output as YAML instead of JSON
confixer show config.yaml --format yaml
```

## Validate Configuration

Validate configuration files:

```bash
# Basic syntax validation
confixer validate config.yaml

# Validate against Pydantic schema
confixer validate config.yaml --schema myapp.config:AppConfig

# Validate against dataclass schema
confixer validate config.yaml --schema myapp.models:Settings
```

## Real-World Examples

### Development vs Production

Development configuration:
```bash
# Show development config with debug settings
APP_DEBUG=true APP_LOG_LEVEL=DEBUG confixer show config.yaml --prefix APP_
```

Production configuration:
```bash
# Show production config with environment overrides
confixer show config.yaml --env .env.prod --format yaml
```

### Database Connection Testing

```bash
# Test database connection settings
confixer show config.yaml --path database --set database.host=localhost --set database.port=5432
```

### API Configuration

```bash
# Show API settings with runtime port override
confixer show config.yaml --path api --set api.port=8080
```

### Multi-Environment Setup

```bash
# Development
confixer show config.yaml --env .env.dev --prefix DEV_

# Staging  
confixer show config.yaml --env .env.staging --prefix STAGING_

# Production
confixer show config.yaml --env .env.prod --prefix PROD_
```

## Environment Variable Examples

Set these environment variables before running `confixer show`:

```bash
# Basic variables
export APP_DEBUG=true
export APP_LOG_LEVEL=DEBUG
export APP_ENVIRONMENT=development

# Nested variables (using __ separator)
export DB__HOST=localhost
export DB__PORT=5432
export DB__USER=devuser
export DB__PASSWORD=devpass123

# API configuration
export API__HOST=0.0.0.0
export API__PORT=8080
export API__WORKERS=2

# Cache settings
export CACHE__REDIS__HOST=redis.dev.local
export CACHE__REDIS__PORT=6379
export CACHE__REDIS__TTL=3600
```

Then run:
```bash
confixer show config.yaml --prefix APP_
# or
confixer show config.yaml  # (loads all environment variables)
```

## Tips & Tricks

### 1. Preview Changes Before Deployment
```bash
# See how production environment variables will override your config
confixer show config.yaml --env .env.prod --format yaml > preview.yaml
```

### 2. Extract Specific Service Configurations
```bash
# Get just database config for database tools
confixer show config.yaml --path database --format json > db-config.json

# Get just API config for load balancer setup
confixer show config.yaml --path api --format yaml > api-config.yaml
```

### 3. Validate Before Deployment
```bash
# Validate with all environment overrides
confixer validate <(confixer show config.yaml --env .env.prod --format yaml) --schema myapp:Config
```

### 4. Debug Configuration Issues
```bash
# See the complete merged configuration
confixer show config.yaml --env .env --format yaml

# Check specific problematic path
confixer show config.yaml --env .env --path problematic.nested.key
```
