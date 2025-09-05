# ArchiPy Architecture

## Overview

ArchiPy is organized into four main modules, each serving a specific purpose in creating structured, maintainable Python
applications:

1. **Adapters**: External service integrations
2. **Configs**: Configuration management
3. **Helpers**: Utility functions and support classes
4. **Models**: Core data structures

This architecture follows clean architecture principles, separating concerns and ensuring that dependencies point inward
toward the domain core.

## Modules

### Adapters

The `adapters` module provides implementations for external service integrations, following the Ports and Adapters
pattern (Hexagonal Architecture). This module includes:

- **Base Adapters**: Core implementations and interfaces
    - SQLAlchemy base components
    - Common adapter patterns
    - Base session management

- **Database Adapters**: Database-specific implementations
    - PostgreSQL
    - SQLite
    - StarRocks
    - Each with their own SQLAlchemy integration

- **Service Adapters**: External service integrations
    - Email service adapters
    - External API clients
    - File storage adapters (MinIO)
    - Message brokers (Kafka)
    - Caching systems (Redis)

Each adapter includes both concrete implementations and corresponding mocks for testing.

### Configs

The `configs` module manages configuration loading, validation, and injection. It provides:

- Environment-based configuration
- Type-safe configuration through Pydantic models
- Centralized access to configuration values
- Support for various configuration sources (environment variables, files, etc.)

### Helpers

The `helpers` module contains utility functions and classes to simplify common development tasks. It includes several
subgroups:

- **Utils**: General utility functions for dates, strings, errors, files, etc.
- **Decorators**: Function and class decorators for aspects like logging, timing, and deprecation
- **Interceptors**: Classes for cross-cutting concerns like logging, tracing, and validation
- **Validators**: Data validation utilities

### Models

The `models` module defines the core data structures used throughout the application:

- **Entities**: Domain model objects
- **DTOs**: Data Transfer Objects for API input/output
- **Errors**: Custom exception classes
- **Types**: Type definitions and enumerations

## Architectural Flow

ArchiPy applications follow a clean architecture approach where:

1. The Models module forms the core domain layer
2. The Helpers module provides supporting functionality
3. The Configs module manages application configuration
4. The Adapters module interfaces with external systems

This modular organization promotes separation of concerns, making ArchiPy applications easier to test, maintain, and
extend over time.

## Design Philosophy

ArchiPy is designed to standardize and simplify Python application development by providing a flexible set of building
blocks that work across different architectural approaches. Rather than enforcing a single architectural pattern,
ArchiPy offers components that can be applied to:

* Layered Architecture
* Hexagonal Architecture (Ports & Adapters)
* Clean Architecture
* Domain-Driven Design
* Service-Oriented Architecture
* And more...

These building blocks help maintain consistency, testability, and maintainability regardless of the specific
architectural style chosen for your project.

## Core Building Blocks

### Configuration Management

ArchiPy provides a standardized way to manage configuration across your application:

```python
from archipy.configs.base_config import BaseConfig

class AppConfig(BaseConfig):
    DATABASE = {
        "HOST": "localhost",
        "PORT": 5432,
        "USERNAME": "user",
        "PASSWORD": "password"
    }

    DEBUG = True

# Set global configuration
config = AppConfig()
BaseConfig.set_global(config)
```

### Adapters & Ports

ArchiPy implements the ports and adapters pattern to isolate the application core from external dependencies:

```python
# Port: defines an interface (contract)
from typing import Protocol

class UserRepositoryPort(Protocol):
    def get_by_id(self, user_id: str) -> User: ...
    def create(self, user: User) -> User: ...

# Adapter: implements the interface for a specific technology
class SqlAlchemyUserRepository:
    def __init__(self, db_adapter: SqlAlchemyAdapter):
        self.db_adapter = db_adapter

    def get_by_id(self, user_id: str) -> User:
        return self.db_adapter.get_by_uuid(User, user_id)

    def create(self, user: User) -> User:
        return self.db_adapter.create(user)

# Application core uses the port, not the adapter
class UserService:
    def __init__(self, repository: UserRepositoryPort):
        self.repository = repository

    def get_user(self, user_id: str) -> User:
        return self.repository.get_by_id(user_id)
```

### Entity Models

Standardized entity models provide a consistent approach to domain modeling:

```python
from sqlalchemy import Column, String
from archipy.models.entities import BaseEntity

class User(BaseEntity):
    __tablename__ = "users"

    name = Column(String(100))
    email = Column(String(255), unique=True)
```

### Data Transfer Objects (DTOs)

Define consistent data structures for transferring data between layers:

```python
from pydantic import BaseModel, EmailStr
from archipy.models.dtos import BaseDTO

class UserCreateDTO(BaseDTO):
    name: str
    email: EmailStr

class UserResponseDTO(BaseDTO):
    id: str
    name: str
    email: EmailStr
    created_at: datetime
```

## Example Architectures

### Layered Architecture

ArchiPy can be used with a traditional layered architecture approach:

```
┌───────────────────────┐
│     Presentation      │  API, UI, CLI
├───────────────────────┤
│     Application       │  Services, Workflows
├───────────────────────┤
│       Domain          │  Business Logic, Entities
├───────────────────────┤
│    Infrastructure     │  Adapters, Repositories, External Services
└───────────────────────┘
```

### Clean Architecture

ArchiPy supports Clean Architecture principles:

```
┌─────────────────────────────────────────────┐
│                  Entities                    │
│     Domain models, business rules            │
├─────────────────────────────────────────────┤
│                  Use Cases                   │
│     Application services, business workflows │
├─────────────────────────────────────────────┤
│                 Interfaces                   │
│     Controllers, presenters, gateways        │
├─────────────────────────────────────────────┤
│                Frameworks                    │
│     External libraries, UI, DB, devices      │
└─────────────────────────────────────────────┘
```

### Hexagonal Architecture

For projects using a Hexagonal (Ports & Adapters) approach:

```
┌───────────────────────────────────────────────────┐
│                                                   │
│                 Application Core                  │
│                                                   │
│  ┌─────────────────────────────────────────────┐  │
│  │                                             │  │
│  │           Domain Logic / Models             │  │
│  │                                             │  │
│  └─────────────────────────────────────────────┘  │
│                                                   │
│  ┌─────────────┐         ┌─────────────────────┐  │
│  │             │         │                     │  │
│  │  Input      │         │  Output Ports       │  │
│  │  Ports      │         │                     │  │
│  │             │         │                     │  │
│  └─────────────┘         └─────────────────────┘  │
│                                                   │
└───────────────────────────────────────────────────┘
        ▲                           ▲
        │                           │
        │                           │
┌───────┴──────────┐      ┌────────┴────────────┐
│                  │      │                     │
│  Input Adapters  │      │  Output Adapters    │
│  (Controllers)   │      │  (Repositories,     │
│                  │      │   Clients, etc.)    │
│                  │      │                     │
└──────────────────┘      └─────────────────────┘
```

## Practical Implementation

Let's see how a complete application might be structured using ArchiPy:

```
my_app/
├── configs/
│   └── app_config.py          # Application configuration
├── adapters/
│   ├── db/                    # Database adapters
│   └── api/                   # API adapters
├── core/
│   ├── models/                # Domain models
│   ├── ports/                 # Interface definitions
│   └── services/              # Business logic
├── repositories/              # Data access
├── api/                       # API routes
└── main.py                    # Application entry point
```

## Code Example

Here's how you might structure a FastAPI application using ArchiPy:

```python
# adapters/db/user_repository.py
from archipy.adapters.postgres.sqlalchemy.adapters import SQLAlchemyAdapter
from core.models.user import User


class UserRepository:
    def __init__(self, db_adapter: SQLAlchemyAdapter):
        self.db_adapter = db_adapter

    def get_user_by_id(self, user_id: str) -> User:
        return self.db_adapter.get_by_uuid(User, user_id)

    def create_user(self, user: User) -> User:
        return self.db_adapter.create(user)


# core/services/user_service.py
from core.models.user import User
from adapters.db.user_repository import UserRepository


class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def register_user(self, name: str, email: str) -> User:
        # Business logic and validation here
        user = User(name=name, email=email)
        return self.user_repository.create_user(user)


# api/users.py
from fastapi import APIRouter, Depends
from core.services.user_service import UserService
from archipy.models.dtos import BaseDTO

router = APIRouter()


class UserCreateDTO(BaseDTO):
    name: str
    email: str


@router.post("/users/")
def create_user(
        data: UserCreateDTO,
        user_service: UserService = Depends(get_user_service)
):
    user = user_service.register_user(data.name, data.email)
    return {"id": str(user.test_uuid), "name": user.name, "email": user.email}


# main.py
from fastapi import FastAPI
from archipy.helpers.utils.app_utils import AppUtils
from archipy.configs.base_config import BaseConfig

app = AppUtils.create_fastapi_app(BaseConfig.global_config())
app.include_router(users_router)
```

By providing standardized building blocks rather than enforcing a specific architecture, ArchiPy helps teams maintain
consistent development practices while allowing flexibility to choose the architectural pattern that best fits their
needs.
