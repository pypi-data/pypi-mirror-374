# Redis Adapter Examples

This guide demonstrates how to use the ArchiPy Redis adapter for common caching and key-value storage patterns.

## Basic Usage

### Installation

First, ensure you have the Redis dependencies installed:

```bash
pip install "archipy[redis]"
# or
uv add "archipy[redis]"
```

### Synchronous Redis Adapter

```python


from archipy.adapters.redis.adapters import RedisAdapter
from archipy.models.errors import CacheError

try:
    # Create a Redis adapter with connection details
    redis = RedisAdapter(
        host="localhost",
        port=6379,
        db=0,
        password=None  # Optional
    )

    # Set and get values
    redis.set("user:123:name", "John Doe")
    name = redis.get("user:123:name")
    print(f"User name: {name}")  # Output: User name: John Doe

    # Set with expiration (seconds)
    redis.set("session:456", "active", ex=3600)  # Expires in 1 hour

    # Delete a key
    redis.delete("user:123:name")

    # Check if key exists
    if redis.exists("session:456"):
        print("Session exists")
except CacheError as e:
    print(f"Redis operation failed: {str(e)}")
```

### Asynchronous Redis Adapter

```python
import asyncio
from typing import Optional

from archipy.adapters.redis.adapters import AsyncRedisAdapter
from archipy.models.errors import CacheError


async def main() -> None:
    try:
        # Create an async Redis adapter
        redis = AsyncRedisAdapter(
            host="localhost",
            port=6379,
            db=0
        )

        # Async operations
        await redis.set("counter", "1")
        await redis.incr("counter")  # Increment
        count = await redis.get("counter")
        print(f"Counter: {count}")  # Output: Counter: 2

        # Cleanup
        await redis.close()
    except CacheError as e:
        print(f"Redis operation failed: {str(e)}")


# Run the async function
asyncio.run(main())
```

## Caching Patterns

### Function Result Caching

```python
import json
import time
from functools import wraps
from typing import Any, Callable, TypeVar, cast

from archipy.adapters.redis.adapters import RedisAdapter
from archipy.models.errors import CacheError, CacheMissError

# Define a type variable for generic function types
T = TypeVar('T', bound=Callable[..., Any])

# Create a Redis adapter
redis = RedisAdapter(host="localhost", port=6379, db=0)


def cache_result(key_prefix: str, ttl: int = 300) -> Callable[[T], T]:
    """Decorator to cache function results in Redis.

    Args:
        key_prefix: Prefix for the Redis cache key
        ttl: Time-to-live in seconds (default: 5 minutes)

    Returns:
        Decorated function with Redis caching
    """

    def decorator(func: T) -> T:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Create a cache key with function name and arguments
            cache_key = f"{key_prefix}:{func.__name__}:{hash(str(args) + str(kwargs))}"

            try:
                # Try to get from cache
                cached = redis.get(cache_key)
                if cached:
                    return json.loads(cached)

                # Execute function and cache result
                result = func(*args, **kwargs)
                redis.set(cache_key, json.dumps(result), ex=ttl)
                return result
            except CacheMissError:
                # Execute function if not in cache
                result = func(*args, **kwargs)
                try:
                    redis.set(cache_key, json.dumps(result), ex=ttl)
                except CacheError as e:
                    # Log but don't fail if caching fails
                    print(f"Failed to cache result: {e}")
                return result
            except CacheError as e:
                # Execute function if Redis fails
                print(f"Redis error: {e}")
                return func(*args, **kwargs)

        return cast(T, wrapper)

    return decorator


# Example usage
@cache_result("api", ttl=60)
def expensive_api_call(item_id: int) -> dict[str, Any]:
    """Simulate an expensive API call.

    Args:
        item_id: ID of the item to fetch

    Returns:
        Item data dictionary
    """
    print("Executing expensive operation...")
    time.sleep(1)  # Simulate expensive operation
    return {"id": item_id, "name": f"Item {item_id}", "data": "Some data"}


# First call will execute the function
result1 = expensive_api_call(123)
print("First call:", result1)

# Second call will retrieve from cache
result2 = expensive_api_call(123)
print("Second call:", result2)
```

## Mock Redis for Testing

ArchiPy provides a Redis mock for unit testing that doesn't require a real Redis server:

```python
import unittest
from typing import Optional

from archipy.adapters.redis.adapters import RedisAdapter
from archipy.adapters.redis.mocks import RedisMock
from archipy.models.errors import CacheError, CacheMissError


class UserService:
    def __init__(self, redis_adapter: RedisAdapter) -> None:
        self.redis = redis_adapter

    def get_user(self, user_id: int) -> str:
        """Get user data, either from cache or backend.

        Args:
            user_id: User ID to look up

        Returns:
            User data as a string

        Raises:
            CacheError: If Redis operation fails
        """
        try:
            cache_key = f"user:{user_id}"
            cached = self.redis.get(cache_key)
            if cached:
                return cached

            # In real code, we'd fetch from database if not in cache
            user_data = f"User {user_id} data"
            self.redis.set(cache_key, user_data, ex=300)
            return user_data
        except CacheMissError:
            # Handle cache miss
            user_data = f"User {user_id} data"
            try:
                self.redis.set(f"user:{user_id}", user_data, ex=300)
            except CacheError:
                pass  # Ignore error setting cache
            return user_data


class TestUserService(unittest.TestCase):
    def setUp(self) -> None:
        # Use the RedisMock instead of a real Redis connection
        self.redis_mock = RedisMock()
        self.user_service = UserService(self.redis_mock)

    def test_get_user(self) -> None:
        # Test first fetch (not cached)
        user_data = self.user_service.get_user(123)
        self.assertEqual(user_data, "User 123 data")

        # Test that it was cached
        self.assertEqual(self.redis_mock.get("user:123"), "User 123 data")

        # Change the cached value to test cache hit
        self.redis_mock.set("user:123", "Modified data")

        # Test cached fetch
        user_data = self.user_service.get_user(123)
        self.assertEqual(user_data, "Modified data")


# Run the test
if __name__ == "__main__":
    unittest.main()
```

## Advanced Redis Features

### Publish/Subscribe

```python
import threading
import time
from typing import Dict, Any

from archipy.adapters.redis.adapters import RedisAdapter
from archipy.models.errors import CacheError


# Subscriber thread
def subscribe_thread() -> None:
    try:
        subscriber = RedisAdapter(host="localhost", port=6379, db=0)
        pubsub = subscriber.pubsub()

        def message_handler(message: Dict[str, Any]) -> None:
            if message["type"] == "message":
                print(f"Received message: {message['data']}")

        pubsub.subscribe(**{"channel:notifications": message_handler})
        pubsub.run_in_thread(sleep_time=0.5)

        # Keep thread running for demo
        time.sleep(10)
        pubsub.close()
    except CacheError as e:
        print(f"Redis subscription error: {e}")


try:
    # Start subscriber in background
    thread = threading.Thread(target=subscribe_thread)
    thread.start()

    # Wait for subscriber to initialize
    time.sleep(1)

    # Create publisher
    redis = RedisAdapter(host="localhost", port=6379, db=0)

    # Publish messages
    for i in range(5):
        message = f"Notification {i}"
        redis.publish("channel:notifications", message)
        time.sleep(1)

    # Wait for thread to complete
    thread.join()
except CacheError as e:
    print(f"Redis publisher error: {e}")
except Exception as e:
    print(f"General error: {e}")
```

### Pipeline for Multiple Operations

```python
from typing import List

from archipy.adapters.redis.adapters import RedisAdapter
from archipy.models.errors import CacheError

try:
    redis = RedisAdapter(host="localhost", port=6379, db=0)

    # Create a pipeline for atomic operations
    pipe = redis.pipeline()
    pipe.set("stats:visits", 0)
    pipe.set("stats:unique_users", 0)
    pipe.set("stats:conversion_rate", "0.0")
    pipe.execute()  # Execute all commands at once

    # Increment multiple counters atomically
    pipe = redis.pipeline()
    pipe.incr("stats:visits")
    pipe.incr("stats:unique_users")
    results: List[int] = pipe.execute()
    print(f"Visits: {results[0]}, Unique users: {results[1]}")
except CacheError as e:
    print(f"Redis pipeline error: {e}")
```
