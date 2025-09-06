three-x-pay-sdk
================

Python SDK for the 3X PAY API.

- API reference: [OpenAPI spec](https://app.3xpay.org/api/openapi.json)

Installation
------------

```bash
pip install three-x-pay-sdk
```

Quick start (sync)
-----------

```python
from three_x_pay_sdk import ThreeXPayClient, CreatePayInRequest


client = ThreeXPayClient(api_key="YOUR_API_KEY")

# Health check
client.ping()

# Create payin
req = CreatePayInRequest(
    amount=10.5,
    currency="USDT",
    merchant_order_id="order-123",
    merchant_callback_url="https://example.com/webhook",
    merchant_return_url="https://example.com/return",
    is_test=True,
)
created = client.create_payin(req)
print(created.data.payment_url)

# Get payin
info = client.get_payin(created.data.id)
print(info.data.status)

# Alternatively, use context manager
with ThreeXPayClient(api_key="YOUR_API_KEY") as client:
    client.ping()
```

Webhook signature
-----------------

```python
from three_x_pay_sdk import verify_signature

is_valid = verify_signature(body_bytes, secret_key, signature_from_header)
```

License
-------

MIT
