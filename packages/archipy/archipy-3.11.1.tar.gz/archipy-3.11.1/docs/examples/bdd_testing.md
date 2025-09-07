# BDD Testing with ArchiPy

This page demonstrates how to use ArchiPy's integrated BDD testing capabilities with Behave.

## Basic Usage

ArchiPy provides a complete BDD testing setup using Behave. Here's how to use it:

### Feature Files

Create feature files in the `features` directory with Gherkin syntax:

```gherkin
# features/user_management.feature
Feature: User Management
  As a system administrator
  I want to manage users
  So that I can control system access

  Scenario: Create a new user
    Given I have admin privileges
    When I create a user with username "john" and email "john@example.com"
    Then the user should be saved in the database
    And the user should have default permissions
```

### Step Implementations

Implement the steps in Python files under `features/steps`:

```python
# features/steps/user_steps.py
from typing import Any
from behave import given, when, then
from app.models import User
from app.services import UserService
from archipy.models.errors import NotFoundError, DatabaseQueryError

@given('I have admin privileges')
def step_impl(context: Any) -> None:
    context.is_admin = True

@when('I create a user with username "{username}" and email "{email}"')
def step_impl(context: Any, username: str, email: str) -> None:
    service = UserService()
    try:
        context.user = service.create_user(username, email)
    except Exception as e:
        # Proper exception chaining
        raise DatabaseQueryError(
            additional_data={"username": username, "email": email}
        ) from e

@then('the user should be saved in the database')
def step_impl(context: Any) -> None:
    # Check user exists in DB
    try:
        db_user = User.query.filter_by(username=context.user.username).first()
        assert db_user is not None
    except Exception as e:
        raise NotFoundError(
            resource_type="user",
            additional_data={"username": context.user.username}
        ) from e

@then('the user should have default permissions')
def step_impl(context: Any) -> None:
    assert len(context.user.permissions) > 0
    assert 'user:read' in context.user.permissions
```

### Running Tests

Run BDD tests using the Makefile command:

```bash
make behave
```

To run a specific feature:

```bash
uv run behave features/user_management.feature
```

To run a specific scenario by line number:

```bash
uv run behave features/user_management.feature:7
```

## Advanced BDD Testing

### Using Context Tables

Behave supports data tables for testing multiple scenarios:

```gherkin
Scenario: Create multiple users
Given I have admin privileges
When I create the following users:
| username | email              | role    |
| john     | john@example.com   | user    |
| alice    | alice@example.com  | admin   |
| bob      | bob@example.com    | support |
Then all users should be saved in the database
```

```python
@when('I create the following users')
def step_impl(context: Any) -> None:
    service = UserService()
    context.users = []
    for row in context.table:
        try:
            user = service.create_user(
                username=row['username'],
                email=row['email'],
                role=row['role']
            )
            context.users.append(user)
        except Exception as e:
            raise DatabaseQueryError(
                additional_data={"username": row['username'], "email": row['email']}
            ) from e
```
