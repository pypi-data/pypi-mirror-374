# Email Adapter Examples

This page demonstrates how to use ArchiPy's email adapter functionality.

## Basic Usage

```python
from archipy.adapters.email import EmailAdapter

# Configure email adapter
email_adapter = EmailAdapter(
    host="smtp.example.com",
    port=587,
    username="your-username",
    password="your-password",
    use_tls=True
)

# Send an email
email_adapter.send_email(
    subject="Test Email",
    body="This is a test email from ArchiPy",
    recipients=["recipient@example.com"],
    cc=["cc@example.com"],
    bcc=["bcc@example.com"],
    from_email="sender@example.com"
)
```

This documentation is being migrated from Sphinx to MkDocs format.
Please check back soon for complete content.
