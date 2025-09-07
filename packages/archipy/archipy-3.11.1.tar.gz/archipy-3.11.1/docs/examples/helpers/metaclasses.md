# Metaclass Examples

This page demonstrates how to use ArchiPy's metaclasses.

## Basic Usage

```python
from archipy.helpers.metaclasses.singleton import Singleton

# Create a singleton class
class Database(metaclass=Singleton):
    def __init__(self, connection_string=None):
        self.connection_string = connection_string
        # Initialize connection

    def query(self, sql):
        # Execute query
        pass

# Usage
db1 = Database("postgresql://localhost:5432/mydb")
db2 = Database()  # No new instance created

print(db1 is db2)  # True - same instance
print(db2.connection_string)  # "postgresql://localhost:5432/mydb"
```

This documentation is being migrated from Sphinx to MkDocs format.
Please check back soon for complete content.
