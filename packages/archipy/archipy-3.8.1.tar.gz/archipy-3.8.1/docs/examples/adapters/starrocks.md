# StarRocks Adapter

This example demonstrates how to use the StarRocks adapter for database operations.

## Basic Usage

```python
from archipy.adapters.starrocks.sqlalchemy.adapters import StarrocksSQLAlchemyAdapter
from archipy.models.entities.sqlalchemy.base_entities import BaseEntity
from sqlalchemy import Column, String, Integer, DateTime

# Define a model
class User(BaseEntity):
    __tablename__ = "users"
    username = Column(String(100), unique=True)
    email = Column(String(255), unique=True)
    age = Column(Integer)
    created_at = Column(DateTime)

# Create adapter
adapter = StarrocksSQLAlchemyAdapter()

# Create tables
BaseEntity.metadata.create_all(adapter.session_manager.engine)

# Basic operations
with adapter.session() as session:
    # Create
    user = User(
        username="john_doe",
        email="john@example.com",
        age=30,
        created_at=datetime.now()
    )
    session.add(user)
    session.commit()

    # Read
    user = session.query(User).filter_by(username="john_doe").first()
    print(user.email)  # john@example.com

    # Update
    user.age = 31
    session.commit()

    # Delete
    session.delete(user)
    session.commit()
```

## Using Transactions

```python
from archipy.helpers.decorators.sqlalchemy_atomic import starrocks_sqlalchemy_atomic_decorator

@starrocks_sqlalchemy_atomic_decorator
def create_user_with_profile(username, email, age, profile_data):
    user = User(username=username, email=email, age=age)
    adapter.create(user)

    profile = Profile(user_id=user.test_uuid, **profile_data)
    adapter.create(profile)

    return user
```

## Async Operations

```python
from archipy.adapters.starrocks.sqlalchemy.adapters import AsyncStarrocksSQLAlchemyAdapter
from archipy.helpers.decorators.sqlalchemy_atomic import async_starrocks_sqlalchemy_atomic_decorator

async def main():
    adapter = AsyncStarrocksSQLAlchemyAdapter()

    @async_starrocks_sqlalchemy_atomic_decorator
    async def create_user_async(username, email, age):
        user = User(username=username, email=email, age=age)
        return await adapter.create(user)

    user = await create_user_async("jane_doe", "jane@example.com", 28)
    print(user.username)  # jane_doe
```

## Error Handling

```python
from archipy.models.errors import (
    AlreadyExistsError,
    NotFoundError,
    InternalError
)

try:
    user = adapter.get_by_id(User, user_id)
    if not user:
        raise NotFoundError(resource_type="user")
except AlreadyExistsError as e:
    print(f"User already exists: {e.message}")
except InternalError as e:
    print(f"Database error: {e.message}")
```

## Advanced Queries

```python
# Complex filtering
users = adapter.query(User).filter(
    User.age > 25,
    User.created_at >= datetime.now() - timedelta(days=30)
).all()

# Aggregation
from sqlalchemy import func
age_stats = adapter.query(
    func.avg(User.age).label('avg_age'),
    func.max(User.age).label('max_age'),
    func.min(User.age).label('min_age')
).first()

# Joins
from sqlalchemy import join
user_profiles = adapter.query(User).join(
    Profile,
    User.test_uuid == Profile.user_id
).all()
```

## Batch Operations

```python
# Batch insert
users = [
    User(username=f"user{i}", email=f"user{i}@example.com", age=20+i)
    for i in range(100)
]
adapter.bulk_create(users)

# Batch update
adapter.query(User).filter(User.age < 30).update(
    {"age": User.age + 1},
    synchronize_session=False
)
```

## Configuration

```python
from archipy.configs.config_template import StarrocksConfig

# Configure StarRocks connection
config = StarrocksConfig(
    HOST="localhost",
    PORT=9030,
    USER="root",
    PASSWORD="password",
    DATABASE="test_db"
)

# Create adapter with custom config
adapter = StarrocksSQLAlchemyAdapter(config=config)
```
