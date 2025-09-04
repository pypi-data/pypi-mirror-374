# Getting Started

This guide will help you start building applications with ArchiPy.

## Basic Setup

1. First, initialize your application with a configuration:

```python
from archipy.configs.base_config import BaseConfig

class AppConfig(BaseConfig):
    # Custom configuration
    pass

# Set as global config
config = AppConfig()
BaseConfig.set_global(config)
```

2. Define your domain models:

```python
from uuid import uuid4
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from archipy.models.entities.sqlalchemy.base_entities import BaseEntity

class User(BaseEntity):
    __tablename__ = "users"

    username = Column(String(100), unique=True)
    email = Column(String(255), unique=True)

    # Relationships
    posts = relationship("Post", back_populates="author")

class Post(BaseEntity):
    __tablename__ = "posts"

    title = Column(String(255))
    content = Column(String(1000))

    # Foreign keys
    author_id = Column(UUID, ForeignKey("users.test_uuid"))

    # Relationships
    author = relationship("User", back_populates="posts")
```

3. Set up your database adapter:

```python
# For PostgreSQL
from archipy.adapters.postgres.sqlalchemy.adapters import PostgresSQLAlchemyAdapter, AsyncPostgresSQLAlchemyAdapter

# For SQLite
from archipy.adapters.sqlite.sqlalchemy.adapters import SQLiteSQLAlchemyAdapter, AsyncSQLiteSQLAlchemyAdapter

# For StarRocks
from archipy.adapters.starrocks.sqlalchemy.adapters import StarrocksSQLAlchemyAdapter, AsyncStarrocksSQLAlchemyAdapter

# Create adapter (uses global config)
db_adapter = PostgresSQLAlchemyAdapter()

# Create tables (development only)
BaseEntity.metadata.create_all(db_adapter.session_manager.engine)
```

4. Implement your repositories:

```python
from sqlalchemy import select
from archipy.models.dtos.pagination_dto import PaginationDTO
from archipy.models.dtos.sort_dto import SortDTO

class UserRepository:
    def __init__(self, db_adapter):
        self.db_adapter = db_adapter

    def create(self, username, email):
        user = User(test_uuid=uuid4(), username=username, email=email)
        return self.db_adapter.create(user)

    def get_by_username(self, username):
        query = select(User).where(User.username == username)
        users, _ = self.db_adapter.execute_search_query(User, query)
        return users[0] if users else None

    def search_users(self, search_term: str | None = None,
                    pagination: PaginationDTO | None = None,
                    sort: SortDTO | None = None):
        query = select(User)
        if search_term:
            query = query.where(User.username.ilike(f"%{search_term}%"))
        return self.db_adapter.execute_search_query(User, query, pagination, sort)
```

5. Implement your business logic:

```python
from archipy.models.errors import AlreadyExistsError

class UserService:
    def __init__(self, user_repository):
        self.user_repository = user_repository

    def register_user(self, username, email):
        # Check if user exists
        existing_user = self.user_repository.get_by_username(username)
        if existing_user:
            raise AlreadyExistsError(
                resource_type="user",
                additional_data={"username": username}
            )

        # Create new user
        return self.user_repository.create(username, email)
```

## Working with Redis

For caching or other Redis operations:

```python
from archipy.adapters.redis.adapters import RedisAdapter, AsyncRedisAdapter

# Create Redis adapter (uses global config)
redis_adapter = RedisAdapter()

# Cache user data
def cache_user(user):
    user_data = {
        "username": user.username,
        "email": user.email
    }
    redis_adapter.set(f"user:{user.test_uuid}", json.dumps(user_data), ex=3600)

# Get cached user
def get_cached_user(user_id):
    data = redis_adapter.get(f"user:{user_id}")
    return json.loads(data) if data else None
```

## Working with Keycloak

For authentication and authorization:

```python
from archipy.adapters.keycloak.adapters import KeycloakAdapter, AsyncKeycloakAdapter

# Create Keycloak adapter (uses global config)
keycloak = KeycloakAdapter()

# Authenticate user
token = keycloak.get_token("username", "password")

# Validate token
is_valid = keycloak.validate_token(token["access_token"])

# Get user info
user_info = keycloak.get_userinfo(token["access_token"])
```

## Working with MinIO

For object storage operations:

```python
from archipy.adapters.minio.adapters import MinioAdapter

# Create MinIO adapter (uses global config)
minio = MinioAdapter()

# Create bucket
if not minio.bucket_exists("my-bucket"):
    minio.make_bucket("my-bucket")

# Upload file
minio.put_object("my-bucket", "document.pdf", "/path/to/file.pdf")

# Generate download URL
download_url = minio.presigned_get_object("my-bucket", "document.pdf", expires=3600)
```
