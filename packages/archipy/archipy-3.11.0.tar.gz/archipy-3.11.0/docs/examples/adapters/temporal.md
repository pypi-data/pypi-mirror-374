# Temporal Adapter

This example demonstrates how to use the Temporal adapter for workflow orchestration and activity execution.

## Basic Usage

```python
from typing import Any
from archipy.adapters.temporal import TemporalAdapter, BaseWorkflow, BaseActivity
from archipy.configs.config_template import TemporalConfig
from temporalio import workflow, activity

# Configure Temporal connection with all available settings
temporal_config = TemporalConfig(
    # Connection settings
    HOST="localhost",
    PORT=7233,
    NAMESPACE="default",
    TASK_QUEUE="my-task-queue",

    # TLS settings (optional - for secure connections)
    TLS_CA_CERT="/path/to/ca.crt",
    TLS_CLIENT_CERT="/path/to/client.crt",
    TLS_CLIENT_KEY="/path/to/client.key",

    # Workflow timeout settings (in seconds)
    WORKFLOW_EXECUTION_TIMEOUT=300,  # Maximum total workflow execution time
    WORKFLOW_RUN_TIMEOUT=60,         # Maximum single workflow run time
    WORKFLOW_TASK_TIMEOUT=30,        # Maximum workflow task processing time

    # Activity timeout settings (in seconds)
    ACTIVITY_START_TO_CLOSE_TIMEOUT=30,  # Maximum activity execution time
    ACTIVITY_HEARTBEAT_TIMEOUT=10,       # Activity heartbeat timeout

    # Retry configuration for failed activities
    RETRY_MAXIMUM_ATTEMPTS=3,        # Maximum number of retry attempts
    RETRY_BACKOFF_COEFFICIENT=2.0,   # Backoff multiplier between retries
    RETRY_MAXIMUM_INTERVAL=60        # Maximum interval between retries
)

# Create adapter
temporal = TemporalAdapter(temporal_config)


# Define a simple workflow
class MyWorkflow(BaseWorkflow[dict, str]):
    @workflow.run
    async def run(self, workflow_input: dict) -> str:
        """Main workflow logic.

        Args:
            workflow_input: Input data for the workflow

        Returns:
            Result message from the workflow
        """
        self._log_workflow_event("workflow_started", {"input": workflow_input})

        # Execute an activity - configuration is automatically applied from TemporalConfig
        result = await self._execute_activity_with_retry(
            process_data_activity,
            workflow_input
            # start_to_close_timeout, heartbeat_timeout, retry_policy, task_queue
            # are automatically set from TemporalConfig if not provided
        )

        self._log_workflow_event("workflow_completed", {"result": result})
        return f"Workflow completed: {result}"


# Define a simple activity function
@activity.defn
async def process_data_activity(data: dict) -> str:
    """Process data in an activity.

    Args:
        data: Input data to process

    Returns:
        Processed result
    """
    # Simulate processing
    import time
    time.sleep(1)
    return f"Processed {len(data)} items"


# Execute workflow
async def main():
    try:
        # Execute workflow and wait for result
        result = await temporal.execute_workflow(
            MyWorkflow,
            {"items": ["a", "b", "c"]},
            workflow_id="my-workflow-123",
            task_queue="my-task-queue"
        )
        print(f"Workflow result: {result}")
    finally:
        await temporal.close()

# Run the workflow
import asyncio
asyncio.run(main())


## Configuration Override Examples

```python
from datetime import timedelta
from temporalio.common import RetryPolicy

class ConfigOverrideWorkflow(BaseWorkflow[dict, str]):
    @workflow.run
    async def run(self, workflow_input: dict) -> str:
        """Workflow showing how to override default configurations."""

        # Override activity timeout for a long-running activity
        long_result = await self._execute_activity_with_retry(
            long_running_activity,
            workflow_input,
            start_to_close_timeout=timedelta(minutes=10),  # Override default 30 seconds
            heartbeat_timeout=timedelta(seconds=30)        # Override default 10 seconds
        )

        # Override retry policy for a critical activity
        critical_result = await self._execute_activity_with_retry(
            critical_activity,
            workflow_input,
            retry_policy=RetryPolicy(
                maximum_attempts=10,        # Override default 3 attempts
                backoff_coefficient=1.5,   # Override default 2.0
                maximum_interval=timedelta(seconds=30)  # Override default 60 seconds
            )
        )

        # Use custom task queue
        special_result = await self._execute_activity_with_retry(
            special_activity,
            workflow_input,
            task_queue="special-workers"  # Override default task queue
        )

        # Execute child workflow with custom timeout
        child_result = await self._execute_child_workflow(
            ChildWorkflow,
            {"parent_data": workflow_input},
            execution_timeout=timedelta(minutes=15)  # Override default 5 minutes
        )

        return f"All results: {long_result}, {critical_result}, {special_result}, {child_result}"


@activity.defn
async def long_running_activity(data: dict) -> str:
    """Activity that takes a long time to complete."""
    # Simulate long-running work
    await asyncio.sleep(300)  # 5 minutes
    return f"Long work completed: {data}"


@activity.defn
async def critical_activity(data: dict) -> str:
    """Critical activity that needs more retry attempts."""
    # Simulate critical operation that might fail
    if random.random() < 0.8:  # 80% failure rate for demo
        raise Exception("Critical operation failed")
    return f"Critical work completed: {data}"


@activity.defn
async def special_activity(data: dict) -> str:
    """Activity that runs on special workers."""
    return f"Special work completed: {data}"


class ChildWorkflow(BaseWorkflow[dict, str]):
    @workflow.run
    async def run(self, workflow_input: dict) -> str:
        """Child workflow with its own logic."""
        return f"Child workflow processed: {workflow_input['parent_data']}"
```

## Environment-Based Configuration

```python
import os
from archipy.configs.config_template import TemporalConfig

# Production configuration
production_config = TemporalConfig(
    HOST=os.getenv("TEMPORAL_HOST", "temporal.production.com"),
    PORT=int(os.getenv("TEMPORAL_PORT", "7233")),
    NAMESPACE=os.getenv("TEMPORAL_NAMESPACE", "production"),
    TASK_QUEUE=os.getenv("TEMPORAL_TASK_QUEUE", "production-queue"),

    # Production TLS settings
    TLS_CA_CERT=os.getenv("TEMPORAL_TLS_CA_CERT"),
    TLS_CLIENT_CERT=os.getenv("TEMPORAL_TLS_CLIENT_CERT"),
    TLS_CLIENT_KEY=os.getenv("TEMPORAL_TLS_CLIENT_KEY"),

    # Production timeout settings (longer timeouts)
    WORKFLOW_EXECUTION_TIMEOUT=1800,  # 30 minutes
    WORKFLOW_RUN_TIMEOUT=600,         # 10 minutes
    ACTIVITY_START_TO_CLOSE_TIMEOUT=120,  # 2 minutes

    # Production retry settings (more aggressive)
    RETRY_MAXIMUM_ATTEMPTS=5,
    RETRY_BACKOFF_COEFFICIENT=1.5,
    RETRY_MAXIMUM_INTERVAL=300  # 5 minutes
)

# Development configuration
development_config = TemporalConfig(
    HOST="localhost",
    PORT=7233,
    NAMESPACE="development",
    TASK_QUEUE="dev-queue",

    # Development timeout settings (shorter timeouts for faster feedback)
    WORKFLOW_EXECUTION_TIMEOUT=120,  # 2 minutes
    WORKFLOW_RUN_TIMEOUT=60,         # 1 minute
    ACTIVITY_START_TO_CLOSE_TIMEOUT=30,  # 30 seconds

    # Development retry settings (fewer retries for faster failures)
    RETRY_MAXIMUM_ATTEMPTS=2,
    RETRY_BACKOFF_COEFFICIENT=2.0,
    RETRY_MAXIMUM_INTERVAL=30  # 30 seconds
)

# Select config based on environment
config = production_config if os.getenv("ENV") == "production" else development_config
temporal = TemporalAdapter(config)
```
```

## Using Atomic Activities

Activities can use atomic transactions for database operations:

```python
from archipy.adapters.temporal import AtomicActivity
from archipy.helpers.decorators.sqlalchemy_atomic import postgres_sqlalchemy_atomic_decorator
from archipy.models.errors import DatabaseQueryError, DatabaseConnectionError


# Define an activity with atomic transaction support
class UserCreationActivity(AtomicActivity[dict, dict]):
    def __init__(self, user_service):
        """Initialize with your business logic service.

        Args:
            user_service: Service containing business logic and repository access
        """
        super().__init__(user_service, db_type="postgres")

    async def _do_execute(self, activity_input: dict) -> dict:
        """Create user with atomic transaction.

        Args:
            activity_input: User data to create

        Returns:
            Created user information

        Raises:
            DatabaseQueryError: If database operation fails
            DatabaseConnectionError: If database connection fails
        """
        try:
            # Execute business logic with atomic transaction
            user = await self._call_atomic_method("create_user", activity_input)

            # Additional database operations within the same transaction
            profile = await self._call_atomic_method(
                "create_user_profile",
                user.uuid,
                activity_input.get("profile", {})
            )

            return {
                "user_id": str(user.uuid),
                "username": user.username,
                "profile_id": str(profile.uuid)
            }
        except Exception as e:
            self._log_activity_event("user_creation_failed", {
                "error": str(e),
                "input": activity_input
            })
            raise


# Use in workflow
class UserOnboardingWorkflow(BaseWorkflow[dict, dict]):
    @workflow.run
    async def run(self, workflow_input: dict) -> dict:
        """User onboarding workflow.

        Args:
            workflow_input: User registration data

        Returns:
            Onboarding result
        """
        self._log_workflow_event("onboarding_started")

        # Execute atomic user creation activity
        user_result = await self._execute_activity_with_retry(
            UserCreationActivity.execute_atomic,
            workflow_input["user_data"],
            start_to_close_timeout=timedelta(seconds=60)
        )

        # Execute welcome email activity
        email_result = await self._execute_activity_with_retry(
            send_welcome_email_activity,
            {
                "user_id": user_result["user_id"],
                "email": workflow_input["user_data"]["email"]
            }
        )

        self._log_workflow_event("onboarding_completed", {
            "user_id": user_result["user_id"]
        })

        return {
            "user": user_result,
            "email_sent": email_result
        }
```

## Async Operations with Workers

```python
from archipy.adapters.temporal import TemporalWorkerManager
from archipy.models.errors.temporal_errors import WorkerConnectionError, WorkerShutdownError


async def run_worker():
    """Start a Temporal worker to execute workflows and activities."""
    worker_manager = TemporalWorkerManager()

    try:
        # Start worker with workflows and activities
        worker_handle = await worker_manager.start_worker(
            task_queue="my-task-queue",
            workflows=[MyWorkflow, UserOnboardingWorkflow],
            activities=[UserCreationActivity, process_data_activity, send_welcome_email_activity],
            max_concurrent_workflow_tasks=10,
            max_concurrent_activities=20
        )

        print(f"Worker started: {worker_handle.identity}")

        # Keep worker running
        await worker_handle.wait_until_stopped()

    except WorkerConnectionError as e:
        print(f"Failed to start worker: {e}")
        raise
    except WorkerShutdownError as e:
        print(f"Worker shutdown error: {e}")
        raise
    finally:
        # Graceful shutdown
        await worker_manager.shutdown_all_workers()


# Activity with business logic integration
@activity.defn
async def send_welcome_email_activity(data: dict) -> bool:
    """Send welcome email activity.

    Args:
        data: Email data containing user_id and email

    Returns:
        True if email sent successfully
    """
    # This would integrate with your email service
    print(f"Sending welcome email to {data['email']}")
    return True
```

## Error Handling

```python
from archipy.models.errors.temporal_errors import (
    TemporalError,
    WorkerConnectionError,
    WorkerShutdownError
)
from archipy.models.errors import (
    DatabaseQueryError,
    DatabaseConnectionError,
    NotFoundError
)


async def robust_workflow_execution():
    """Example of proper error handling with Temporal operations."""
    temporal = TemporalAdapter()

    try:
        # Start workflow with error handling
        workflow_handle = await temporal.start_workflow(
            UserOnboardingWorkflow,
            {
                "user_data": {
                    "username": "john_doe",
                    "email": "john@example.com",
                    "profile": {"age": 30, "city": "New York"}
                }
            },
            workflow_id="user-onboarding-001",
            execution_timeout=300,  # 5 minutes
            run_timeout=120         # 2 minutes per run
        )

        # Wait for result with timeout
        result = await workflow_handle.result()
        print(f"User onboarded successfully: {result}")

    except WorkerConnectionError as e:
        print(f"Worker connection failed: {e}")
        # Handle worker connectivity issues
        raise
    except WorkerShutdownError as e:
        print(f"Worker shutdown error: {e}")
        # Handle worker shutdown issues
        raise
    except TemporalError as e:
        print(f"Temporal operation failed: {e}")
        # Handle other temporal-specific errors
        raise
    except (DatabaseQueryError, DatabaseConnectionError) as e:
        print(f"Database error in workflow: {e}")
        # Handle database errors from activities
        raise
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise
    finally:
        # Always cleanup
        await temporal.close()


# Activity-level error handling
class RobustUserActivity(AtomicActivity[dict, dict]):
    def __init__(self, user_service, db_type: str = "postgres"):
        super().__init__(user_service, db_type)

    async def _do_execute(self, activity_input: dict) -> dict:
        """Execute with comprehensive error handling."""
        try:
            return await self._execute_with_atomic("process_user_data", activity_input)
        except DatabaseQueryError as e:
            self._log_activity_event("database_query_failed", {
                "error": str(e),
                "query_type": "user_creation"
            })
            # Re-raise to let Temporal handle retries
            raise
        except DatabaseConnectionError as e:
            self._log_activity_event("database_connection_failed", {
                "error": str(e)
            })
            # This might be retryable
            raise
        except NotFoundError as e:
            self._log_activity_event("resource_not_found", {
                "error": str(e)
            })
            # This is likely not retryable
            raise
        except Exception as e:
            self._log_activity_event("unexpected_error", {
                "error": str(e),
                "error_type": type(e).__name__
            })
            raise

    async def _handle_error(self, activity_input: dict, error: Exception) -> None:
        """Custom error handling for this activity."""
        # Log specific error details
        self._log_activity_event("activity_error_handler", {
            "error_type": type(error).__name__,
            "input_username": activity_input.get("username", "unknown"),
            "retry_attempt": getattr(error, "attempt_count", "unknown")
        })

        # Call parent error handler
        await super()._handle_error(activity_input, error)
```

## Advanced Configuration

```python
from archipy.adapters.temporal import TemporalAdapter
from temporalio.client import TLSConfig


async def configure_temporal_with_tls():
    """Configure Temporal with TLS and advanced settings."""
    # TLS Configuration (files should exist)
    temporal_config = TemporalConfig(
        HOST="temporal.example.com",
        PORT=7233,
        NAMESPACE="production",
        TASK_QUEUE="production-queue",
        TLS_CA_CERT="/path/to/ca.crt",
        TLS_CLIENT_CERT="/path/to/client.crt",
        TLS_CLIENT_KEY="/path/to/client.key",
        # Retry configuration
        RETRY_MAXIMUM_ATTEMPTS=5,
        RETRY_BACKOFF_COEFFICIENT=2.0,
        RETRY_MAXIMUM_INTERVAL=60,
        # Timeout configuration
        WORKFLOW_EXECUTION_TIMEOUT=1800,  # 30 minutes
        WORKFLOW_RUN_TIMEOUT=600,         # 10 minutes
        WORKFLOW_TASK_TIMEOUT=30          # 30 seconds
    )

    temporal = TemporalAdapter(temporal_config)

    try:
        # Query workflow status
        workflow_handle = await temporal.get_workflow_handle("user-onboarding-001")
        description = await workflow_handle.describe()

        print(f"Workflow status: {description.status}")
        print(f"Started at: {description.start_time}")

        # Send signal to workflow
        await temporal.signal_workflow(
            "user-onboarding-001",
            "update_user_status",
            {"status": "verified"}
        )

        # Query workflow for information
        result = await temporal.query_workflow(
            "user-onboarding-001",
            "get_current_status"
        )
        print(f"Current status: {result}")

    finally:
        await temporal.close()
```

## Testing with Mocks

```python
import pytest
from unittest.mock import AsyncMock, MagicMock
from archipy.adapters.temporal import TemporalAdapter


class MockTemporalAdapter(TemporalAdapter):
    """Mock Temporal adapter for testing."""

    def __init__(self):
        # Skip the real initialization
        self.config = MagicMock()
        self._client = AsyncMock()

    async def execute_workflow(self, workflow, arg=None, **kwargs):
        """Mock workflow execution."""
        # Simulate workflow execution
        if workflow == UserOnboardingWorkflow:
            return {
                "user": {"user_id": "test-123", "username": "test_user"},
                "email_sent": True
            }
        return "mock_result"


@pytest.mark.asyncio
async def test_user_onboarding_workflow():
    """Test user onboarding workflow with mock adapter."""
    mock_temporal = MockTemporalAdapter()

    result = await mock_temporal.execute_workflow(
        UserOnboardingWorkflow,
        {
            "user_data": {
                "username": "test_user",
                "email": "test@example.com"
            }
        }
    )

    assert result["user"]["username"] == "test_user"
    assert result["email_sent"] is True


# Mock activity for testing
class MockUserActivity(AtomicActivity[dict, dict]):
    def __init__(self):
        # Initialize with mock logic
        mock_service = MagicMock()
        super().__init__(mock_service)

    async def _do_execute(self, activity_input: dict) -> dict:
        """Mock activity execution."""
        return {
            "user_id": "mock-user-123",
            "username": activity_input["username"]
        }


@pytest.mark.asyncio
async def test_atomic_activity():
    """Test atomic activity with mock."""
    activity = MockUserActivity()

    result = await activity.execute({
        "username": "test_user",
        "email": "test@example.com"
    })

    assert result["username"] == "test_user"
    assert "user_id" in result
```

## Best Practices

1. **Workflow Design**: Keep workflows as coordinators - let activities handle business logic
2. **Error Handling**: Use specific error types and proper error chains
3. **Transactions**: Use `AtomicActivity` for database operations requiring consistency or use Atomic decorators
4. **Testing**: Mock adapters and activities for unit testing
5. **Configuration**: Use environment-specific configurations for different deployments
6. **Monitoring**: Leverage workflow logging and error tracking
7. **Timeouts**: Set appropriate timeouts for workflows and activities
8. **Retries**: Configure retry policies based on error types and business requirements
