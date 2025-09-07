# Parsian Shaparak Payment Gateway

This example demonstrates how to use the Parsian Shaparak payment gateway adapter to process online payments in Iran.

## Configuration

First, configure the Parsian Shaparak settings in your environment or configuration file:

```python
from pydantic import BaseModel
from archipy.configs.base_config import BaseConfig
from archipy.configs.config_template import ParsianShaparakConfig

class MyAppConfig(BaseConfig):
    # Other configuration settings

    # Parsian Shaparak Configuration
    PARSIAN_SHAPARAK: ParsianShaparakConfig = ParsianShaparakConfig(
        LOGIN_ACCOUNT="your_merchant_login_account",
        # Optionally specify custom WSDL URLs if needed
        # PAYMENT_WSDL_URL="https://custom.url/to/payment/wsdl",
        # CONFIRM_WSDL_URL="https://custom.url/to/confirm/wsdl",
        # REVERSAL_WSDL_URL="https://custom.url/to/reversal/wsdl",
        # Optionally specify proxy settings
        # PROXIES={"http": "http://proxy:port", "https": "https://proxy:port"}
    )
```

## Initializing the Adapter

```python
from archipy.adapters.internet_payment_gateways.ir.parsian.adapters import (
    ParsianShaparakPaymentAdapter,
    PaymentRequestDTO,
    ConfirmRequestDTO,
    ConfirmWithAmountRequestDTO,
    ReverseRequestDTO
)

# Initialize the payment adapter
payment_adapter = ParsianShaparakPaymentAdapter()
```

## Processing Payments

### Initiating a Payment

To start a payment transaction:

```python
# Create payment request
payment_request = PaymentRequestDTO(
    amount=10000,  # Amount in IRR (10,000 Rials)
    order_id=12345,  # Your unique order ID
    callback_url="https://your-app.com/payment/callback",  # URL to redirect after payment
    additional_data="Optional additional data",  # Optional
    originator="Optional originator info"  # Optional
)

# Send payment request
payment_response = payment_adapter.initiate_payment(payment_request)

# Check response
if payment_response.status == 0:  # 0 means success in Parsian API
    # Redirect user to payment page
    payment_url = f"https://pec.shaparak.ir/NewIPG/?Token={payment_response.token}"
    # Use this URL to redirect the user to the payment gateway
else:
    # Handle error
    print(f"Payment initiation failed: {payment_response.message}")
```

### Confirming a Payment

After the user completes the payment and returns to your callback URL, confirm the payment:

```python
# Get the token from query parameters in your callback handler
token = 123456789  # This would come from the callback request

# Create confirm request
confirm_request = ConfirmRequestDTO(token=token)

# Confirm payment
confirm_response = payment_adapter.confirm_payment(confirm_request)

if confirm_response.status == 0:  # 0 means success
    # Payment successful
    reference_number = confirm_response.rrn
    masked_card = confirm_response.card_number_masked

    # Process the successful payment in your system
    print(f"Payment confirmed! Reference: {reference_number}, Card: {masked_card}")
else:
    # Handle failed confirmation
    print(f"Payment confirmation failed with status: {confirm_response.status}")
```

### Confirming with Amount Verification

For enhanced security, you can confirm with amount verification:

```python
# Create confirm with amount request
confirm_with_amount_request = ConfirmWithAmountRequestDTO(
    token=123456789,
    order_id=12345,
    amount=10000
)

# Confirm payment with amount verification
confirm_response = payment_adapter.confirm_payment_with_amount(confirm_with_amount_request)

if confirm_response.status == 0:  # 0 means success
    # Payment successful with amount verification
    print(f"Payment confirmed with amount verification!")
else:
    # Handle failed confirmation
    print(f"Payment confirmation failed with status: {confirm_response.status}")
```

### Reversing a Payment

If needed, you can reverse (refund) a successful payment:

```python
# Create reverse request
reverse_request = ReverseRequestDTO(token=123456789)

# Request payment reversal
reverse_response = payment_adapter.reverse_payment(reverse_request)

if reverse_response.status == 0:  # 0 means success
    # Reversal successful
    print(f"Payment reversal successful!")
else:
    # Handle failed reversal
    print(f"Payment reversal failed: {reverse_response.message}")
```

## Error Handling

The adapter uses ArchiPy's error system to provide consistent error handling:

```python
from archipy.models.errors import UnavailableError, InternalError

try:
    payment_response = payment_adapter.initiate_payment(payment_request)
except UnavailableError as e:
    # Handle service unavailable error
    print(f"Payment service unavailable: {e}")
except InternalError as e:
    # Handle unexpected error
    print(f"Unexpected error: {e}")
```

## Complete Example

Here's a complete example integrating the payment flow into a FastAPI application:

```python
from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from typing import Annotated

from archipy.adapters.internet_payment_gateways.ir.parsian.adapters import (
    ParsianShaparakPaymentAdapter,
    PaymentRequestDTO,
    ConfirmRequestDTO
)
from archipy.models.errors import UnavailableError, InternalError

app = FastAPI()
payment_adapter = ParsianShaparakPaymentAdapter()

# Create order model
class OrderCreate(BaseModel):
    amount: int
    order_id: int
    description: str = None

# Payment routes
@app.post("/payments/create")
async def create_payment(order: OrderCreate):
    try:
        payment_request = PaymentRequestDTO(
            amount=order.amount,
            order_id=order.order_id,
            callback_url=f"https://your-app.com/payments/callback",
            additional_data=order.description
        )

        response = payment_adapter.initiate_payment(payment_request)

        if response.status != 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Payment initiation failed: {response.message}"
            )

        # Return payment URL or token
        return {
            "token": response.token,
            "payment_url": f"https://pec.shaparak.ir/NewIPG/?Token={response.token}"
        }

    except UnavailableError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Payment service unavailable"
        )
    except InternalError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@app.get("/payments/callback")
async def payment_callback(token: int, request: Request):
    try:
        confirm_request = ConfirmRequestDTO(token=token)
        confirm_response = payment_adapter.confirm_payment(confirm_request)

        if confirm_response.status == 0:
            # Payment successful - update your database
            return {
                "status": "success",
                "reference_number": confirm_response.rrn,
                "card": confirm_response.card_number_masked
            }
        else:
            return {
                "status": "failed",
                "message": "Payment verification failed"
            }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
```
