# Configuration Management

ArchiPy provides a robust configuration management system that ensures type safety, environment variable support, and
consistent access patterns across your application.

## Basic Configuration

### Defining a Configuration

Create a configuration class by inheriting from `BaseConfig`:

```python
from archipy.configs.base_config import BaseConfig
from archipy.configs.environment_type import EnvironmentType

class AppConfig(BaseConfig):
    # Application settings
    APP_NAME: str = "MyService"
    DEBUG: bool = False

    # Database settings
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "myapp"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "password"

    # Redis settings
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    # Environment
    ENVIRONMENT: EnvironmentType = EnvironmentType.DEV

    # API settings
    API_PREFIX: str = "/api/v1"

    # Logging
    LOG_LEVEL: str = "INFO"
```

### Using the Configuration

```python
# Create and set as global configuration
config = AppConfig()
BaseConfig.set_global(config)

# Access configuration values from anywhere in your code
from archipy.configs.base_config import BaseConfig

current_config = BaseConfig.global_config()
db_url = f"postgresql://{current_config.DB_USER}:{current_config.DB_PASSWORD}@{current_config.DB_HOST}:{current_config.DB_PORT}/{current_config.DB_NAME}"
```

## Environment Variables

ArchiPy configurations automatically load values from environment variables with the same name:

```python
# .env file
APP_NAME = ProductionService
DB_HOST = db.example.com
DB_PASSWORD = secure - password
ENVIRONMENT = PRODUCTION
```

The environment variables override the default values in your configuration class:

```python
config = AppConfig()  # Will have values from environment variables
print(config.APP_NAME)  # "ProductionService"
print(config.ENVIRONMENT)  # EnvironmentType.PRODUCTION
```

## Environment-Specific Configurations

You can create environment-specific configurations:

```python
from archipy.configs.base_config import BaseConfig
from archipy.configs.environment_type import EnvironmentType

class BaseAppConfig(BaseConfig):
    APP_NAME: str = "MyService"
    DEBUG: bool = False
    # Common settings...

class DevelopmentConfig(BaseAppConfig):
    DEBUG: bool = True
    ENVIRONMENT: EnvironmentType = EnvironmentType.DEV
    LOG_LEVEL: str = "DEBUG"

class ProductionConfig(BaseAppConfig):
    DEBUG: bool = False
    ENVIRONMENT: EnvironmentType = EnvironmentType.PRODUCTION
    LOG_LEVEL: str = "WARNING"

# Choose configuration based on environment
import os
env = os.getenv("ENVIRONMENT", "development").lower()

if env == "production":
    config = ProductionConfig()
else:
    config = DevelopmentConfig()

BaseConfig.set_global(config)
```

## Nested Configurations

You can use nested Pydantic models for more complex configurations:

```python
from pydantic import BaseModel
from archipy.configs.base_config import BaseConfig

class DatabaseConfig(BaseModel):
    HOST: str = "localhost"
    PORT: int = 5432
    NAME: str = "myapp"
    USER: str = "postgres"
    PASSWORD: str = "password"

    def connection_string(self) -> str:
        return f"postgresql://{self.USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.NAME}"

class RedisConfig(BaseModel):
    HOST: str = "localhost"
    PORT: int = 6379
    DB: int = 0

class AppConfig(BaseConfig):
    APP_NAME: str = "MyService"
    DEBUG: bool = False
    DATABASE: DatabaseConfig = DatabaseConfig()
    REDIS: RedisConfig = RedisConfig()

# Usage
config = AppConfig()
print(config.DATABASE.connection_string())
```

## Configuration Template

ArchiPy provides pre-configured templates for common configuration objects:

```python
from archipy.configs.base_config import BaseConfig
from archipy.configs.environment_type import EnvironmentType

class AppConfig(BaseConfig):
    # Override only what you need
    APP_NAME: str = "MyCustomApp"

    # The BaseConfig provides default templates for common configurations like:
    # AUTH, DATETIME, ELASTIC, EMAIL, FASTAPI, KAFKA, REDIS, etc.

config = AppConfig()
print(config.ENVIRONMENT)  # Default value from BaseConfig (EnvironmentType.LOCAL)
```

## Configuration in Different Components

### With FastAPI

```python
from fastapi import FastAPI, Depends
from archipy.helpers.utils.app_utils import AppUtils
from archipy.configs.base_config import BaseConfig

# Initialize your configuration
config = BaseConfig()
BaseConfig.set_global(config)

# Create a FastAPI app with configuration
app = AppUtils.create_fastapi_app()  # Uses global config by default

# Or provide a specific configuration
# app = AppUtils.create_fastapi_app(config)

# Access config in endpoint
@app.get("/config")
def get_config_info():
    config = BaseConfig.global_config()
    return {
        "app_name": config.FASTAPI.PROJECT_NAME,
        "environment": config.ENVIRONMENT.value,
        "debug": config.FASTAPI.RELOAD
    }
```

### With Database Adapters

```python
from archipy.adapters.postgres.sqlalchemy.session_managers import SQlAlchemySessionManager
from archipy.configs.base_config import BaseConfig

config = BaseConfig.global_config()

# Create session manager with config
session_manager = SQlAlchemySessionManager(
    connection_string=config.POSTGRES_SQLALCHEMY.POSTGRES_DSN,
    echo=config.POSTGRES_SQLALCHEMY.ECHO
)
```

### With Redis Adapters

```python
from archipy.adapters.redis.adapters import RedisAdapter
from archipy.configs.base_config import BaseConfig

config = BaseConfig.global_config()

# Create Redis adapter with config
redis_adapter = RedisAdapter(
    host=config.REDIS.MASTER_HOST,
    port=config.REDIS.PORT,
    db=config.REDIS.DATABASE
)
```

## Best Practices

1. **Use meaningful defaults**: Configure sensible defaults that work in local development

2. **Never hardcode secrets**: Always use environment variables for sensitive information

3. **Validate configurations**: Use Pydantic validators for complex validation rules

4. **Document configuration options**: Add clear docstrings to your configuration classes

5. **Keep configurations centralized**: Avoid creating multiple configuration sources
