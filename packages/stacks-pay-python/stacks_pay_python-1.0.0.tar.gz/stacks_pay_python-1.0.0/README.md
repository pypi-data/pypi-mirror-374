# sBTC Gateway Python SDK

[![PyPI version](https://badge.fury.io/py/sbtc-gateway.svg)](https://badge.fury.io/py/sbtc-gateway)
[![Python CI](https://github.com/TheSoftNode/sbtc-payment-gateway/workflows/Python%20CI/badge.svg)](https://github.com/TheSoftNode/sbtc-payment-gateway/actions)

Official Python SDK for the sBTC Payment Gateway. Accept Bitcoin and STX payments with ease.

## Features

✅ **Payment Management**: Create, retrieve, list, cancel, and refund payments  
✅ **Merchant API**: Get and update merchant information  
✅ **Webhook Management**: Create and manage webhooks for real-time notifications  
✅ **API Key Management**: Generate and manage API keys  
✅ **Webhook Utils**: Verify webhook signatures securely  
✅ **Error Handling**: Comprehensive error types and handling  
✅ **Type Hints**: Full type hint support for better IDE experience  
✅ **Async Support**: Compatible with async/await patterns  
✅ **Automatic Retries**: Built-in retry logic with exponential backoff  
✅ **Rate Limiting**: Automatic handling of rate limits

## Installation

```bash
pip install sbtc-gateway
```

## Quick Start

```python
import sbtc_gateway

# Initialize the client
client = sbtc_gateway.SBTCGateway('sk_test_your_api_key_here')

# Create a payment
payment = client.payments.create(sbtc_gateway.PaymentRequest(
    amount=50000,  # 0.0005 BTC in satoshis
    currency='sbtc',
    description='Premium subscription',
    customer=sbtc_gateway.Customer(
        email='customer@example.com',
        name='John Doe'
    )
))

print(payment.payment_url)  # Send this URL to your customer
print(payment.qr_code)      # Or show this QR code
```

## API Reference

### Payments

#### Create a Payment

```python
from sbtc_gateway import PaymentRequest, Customer

payment = client.payments.create(PaymentRequest(
    amount=50000,
    currency='sbtc',
    description='Premium subscription',
    customer=Customer(
        email='customer@example.com',
        name='John Doe'
    ),
    webhook_url='https://yoursite.com/webhook',
    redirect_url='https://yoursite.com/success',
    expires_in=3600,  # 1 hour
    metadata={
        'order_id': 'order_123',
        'user_id': '456'
    }
))
```

#### Retrieve a Payment

```python
payment = client.payments.retrieve('payment_id')
```

#### List Payments

```python
result = client.payments.list(
    page=1,
    limit=10,
    status='completed',
    customer_email='customer@example.com'
)

payments = result['payments']
pagination = result['pagination']
```

#### Cancel a Payment

```python
payment = client.payments.cancel('payment_id')
```

#### Refund a Payment

```python
# Full refund
refund = client.payments.refund('payment_id')

# Partial refund
refund = client.payments.refund('payment_id', amount=25000)
```

### Webhooks

#### Create a Webhook

```python
from sbtc_gateway import WebhookRequest

webhook = client.webhooks.create(WebhookRequest(
    url='https://yoursite.com/webhook',
    events=['payment.completed', 'payment.failed'],
    description='Main webhook endpoint'
))
```

#### List Webhooks

```python
result = client.webhooks.list(page=1, limit=10)
webhooks = result['webhooks']
pagination = result['pagination']
```

#### Update a Webhook

```python
webhook = client.webhooks.update('webhook_id', {
    'url': 'https://newsite.com/webhook',
    'events': ['payment.completed']
})
```

#### Delete a Webhook

```python
client.webhooks.delete('webhook_id')
```

#### Test a Webhook

```python
result = client.webhooks.test('webhook_id')
```

#### Get Webhook Statistics

```python
stats = client.webhooks.get_stats('webhook_id')
```

### API Keys

#### Generate an API Key

```python
from sbtc_gateway import APIKeyRequest

result = client.api_keys.generate(APIKeyRequest(
    name='Production API Key',
    permissions=['payments:read', 'payments:write'],
    expires_at='2024-12-31T23:59:59Z'
))

api_key = result['api_key']
key = result['key']  # Save this key securely - it won't be shown again
```

#### List API Keys

```python
result = client.api_keys.list(
    page=1,
    limit=10,
    status='active'
)

api_keys = result['api_keys']
pagination = result['pagination']
```

#### Update an API Key

```python
api_key = client.api_keys.update('key_id', {
    'name': 'Updated Key Name',
    'permissions': ['payments:read']
})
```

#### Deactivate an API Key

```python
api_key = client.api_keys.deactivate('key_id')
```

#### Get API Key Usage

```python
usage = client.api_keys.get_usage('key_id')
```

### Merchant

#### Get Current Merchant

```python
merchant = client.merchant.get_current()
```

#### Update Merchant Information

```python
merchant = client.merchant.update({
    'name': 'Updated Business Name',
    'business_type': 'e-commerce',
    'website': 'https://mybusiness.com',
    'stacks_address': 'SP2J6ZY48GV1EZ5V2V5RB9MP66SW86PYKKNRV9EJ7',
    'bitcoin_address': '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa'
})
```

### Webhook Verification

```python
from sbtc_gateway import WebhookUtils
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook_handler():
    signature = request.headers.get('X-Signature')
    payload = request.get_data(as_text=True)
    secret = 'your_webhook_secret'

    try:
        # Verify the webhook signature
        is_valid = WebhookUtils.verify_signature(payload, signature, secret)

        if not is_valid:
            return jsonify({'error': 'Invalid signature'}), 400

        # Parse the event
        event = WebhookUtils.parse_event(payload)

        # Handle the event
        if event.type == 'payment.completed':
            print(f'Payment completed: {event.data.payment.id}')
        elif event.type == 'payment.failed':
            print(f'Payment failed: {event.data.payment.id}')

        return jsonify({'status': 'success'}), 200

    except Exception as e:
        print(f'Webhook error: {e}')
        return jsonify({'error': 'Error processing webhook'}), 400
```

## Error Handling

```python
from sbtc_gateway import SBTCGateway, SBTCGatewayError, APIError, AuthenticationError

client = SBTCGateway('sk_test_key')

try:
    payment = client.payments.create(payment_data)
except AuthenticationError as e:
    print(f'Authentication failed: {e.message}')
except APIError as e:
    print(f'API Error: {e.message}')
    print(f'Error Code: {e.code}')
    print(f'Details: {e.details}')
except SBTCGatewayError as e:
    print(f'SDK Error: {e.message}')
except Exception as e:
    print(f'Unexpected error: {e}')
```

## Configuration

### Custom Base URL (for testing)

```python
client = SBTCGateway(
    'sk_test_key',
    base_url='https://api.staging.sbtc-gateway.com',
    timeout=60,  # 60 seconds
    retries=5
)
```

### Environment Variables

```bash
export SBTC_GATEWAY_API_KEY=sk_live_your_api_key_here
export SBTC_GATEWAY_BASE_URL=https://api.sbtc-gateway.com
```

```python
import os
from sbtc_gateway import SBTCGateway

client = SBTCGateway(
    os.environ['SBTC_GATEWAY_API_KEY'],
    base_url=os.environ.get('SBTC_GATEWAY_BASE_URL')
)
```

## Django Integration

```python
# settings.py
SBTC_GATEWAY_API_KEY = 'sk_live_your_api_key_here'

# views.py
from django.conf import settings
from sbtc_gateway import SBTCGateway

client = SBTCGateway(settings.SBTC_GATEWAY_API_KEY)

def create_payment(request):
    payment = client.payments.create({
        'amount': 50000,
        'currency': 'sbtc',
        'description': 'Django payment'
    })
    return JsonResponse({'payment_url': payment.payment_url})
```

## FastAPI Integration

```python
from fastapi import FastAPI
from sbtc_gateway import SBTCGateway, PaymentRequest

app = FastAPI()
client = SBTCGateway('sk_test_key')

@app.post("/create-payment")
async def create_payment(payment_data: PaymentRequest):
    payment = client.payments.create(payment_data)
    return {"payment_url": payment.payment_url}
```

## Testing

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=sbtc_gateway
```

## Type Safety

This SDK includes comprehensive type hints for better IDE support:

```python
from sbtc_gateway import (
    SBTCGateway,
    Payment,
    PaymentRequest,
    Webhook,
    APIKey
)

client: SBTCGateway = SBTCGateway('sk_test_key')

# Type-safe payment creation
payment_data: PaymentRequest = PaymentRequest(
    amount=50000,
    currency='sbtc',
    description='Test payment'
)

payment: Payment = client.payments.create(payment_data)
```

## Examples

See the [examples directory](./examples) for complete examples:

- [Basic Payment Flow](./examples/basic_payment.py)
- [Django Integration](./examples/django_example.py)
- [FastAPI Integration](./examples/fastapi_example.py)
- [Webhook Handler](./examples/webhook_handler.py)

## API Compatibility

This SDK is compatible with sBTC Gateway API v1. All endpoints and features are supported:

- **Base URL**: `https://api.sbtc-gateway.com`
- **Authentication**: Bearer token (API key)
- **Format**: JSON REST API
- **Rate Limits**: Automatic handling with retries

## Support

- **Documentation**: [https://docs.sbtc-gateway.com](https://docs.sbtc-gateway.com)
- **Issues**: [GitHub Issues](https://github.com/TheSoftNode/sbtc-payment-gateway/issues)
- **Support**: support@sbtc-gateway.com

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Ensure tests pass: `pytest`
5. Create a pull request

## License

MIT License - see [LICENSE](./LICENSE) file for details.

---

Made with ❤️ by the sBTC Gateway team

Official Python SDK for the sBTC Payment Gateway. Accept Bitcoin and STX payments with ease.

## Installation

```bash
pip install sbtc-gateway
```

## Quick Start

```python
import sbtc_gateway

# Initialize the client
client = sbtc_gateway.SBTCGateway('sk_live_your_api_key_here')

# Create a payment
payment = client.payments.create(sbtc_gateway.PaymentRequest(
    amount=50000,  # 50,000 satoshis
    currency='sbtc',
    description='Premium subscription',
    customer=sbtc_gateway.Customer(
        email='customer@example.com',
        name='John Doe'
    )
))

print(f"Payment URL: {payment.payment_url}")
```

## API Reference

### Initialize Client

```python
import sbtc_gateway

client = sbtc_gateway.SBTCGateway(
    api_key='sk_live_your_api_key_here',
    base_url='https://api.sbtc-gateway.com',  # optional
    timeout=30,  # optional, seconds
    retries=3   # optional, retry attempts
)
```

### Payments API

#### Create Payment

```python
from sbtc_gateway import PaymentRequest, Customer

payment = client.payments.create(PaymentRequest(
    amount=50000,  # Amount in satoshis
    currency='sbtc',  # 'sbtc', 'btc', or 'stx'
    description='Payment description',
    customer=Customer(
        email='customer@example.com',
        name='John Doe'
    ),
    metadata={
        'order_id': 'order_12345',
        'user_id': 'user_67890'
    },
    webhook_url='https://yourapp.com/webhooks/payment',
    redirect_url='https://yourapp.com/success'
))
```

#### Retrieve Payment

```python
payment = client.payments.retrieve('pay_1234567890')
```

#### List Payments

```python
result = client.payments.list(
    page=1,
    limit=20,
    status='completed',
    customer_email='customer@example.com'
)

payments = result.payments
pagination = result.pagination
```

#### Cancel Payment

```python
payment = client.payments.cancel('pay_1234567890')
```

### Merchant API

#### Get Current Merchant

```python
merchant = client.merchant.get_current()
```

#### Update Merchant

```python
merchant = client.merchant.update(
    name='New Business Name',
    website='https://newwebsite.com'
)
```

### Webhook Utilities

#### Verify Webhook Signature

```python
from flask import Flask, request
import sbtc_gateway

app = Flask(__name__)

@app.route('/webhooks/sbtc', methods=['POST'])
def handle_webhook():
    signature = request.headers.get('X-SBTC-Signature')
    payload = request.get_data(as_text=True)
    secret = 'your_webhook_secret'

    try:
        event = sbtc_gateway.WebhookUtils.verify_and_parse_event(
            payload, signature, secret
        )

        if event.type == 'payment.completed':
            print(f'Payment completed: {event.data.payment.id}')
        elif event.type == 'payment.failed':
            print(f'Payment failed: {event.data.payment.id}')

        return 'OK', 200
    except sbtc_gateway.ValidationError as e:
        print(f'Webhook verification failed: {e}')
        return 'Invalid signature', 400
```

## Error Handling

```python
import sbtc_gateway

try:
    payment = client.payments.create(sbtc_gateway.PaymentRequest(
        amount=50000,
        currency='sbtc',
        description='Test payment'
    ))
except sbtc_gateway.AuthenticationError as e:
    print(f'Authentication error: {e.message}')
except sbtc_gateway.ValidationError as e:
    print(f'Validation error: {e.message}')
except sbtc_gateway.APIError as e:
    print(f'API error: {e.message}')
    print(f'Error code: {e.code}')
    print(f'Details: {e.details}')
except sbtc_gateway.NetworkError as e:
    print(f'Network error: {e.message}')
```

## Webhooks

Handle real-time payment updates:

```python
from flask import Flask, request
import sbtc_gateway

app = Flask(__name__)

@app.route('/webhooks/sbtc', methods=['POST'])
def handle_webhook():
    signature = request.headers.get('X-SBTC-Signature')
    payload = request.get_data(as_text=True)

    try:
        event = sbtc_gateway.WebhookUtils.verify_and_parse_event(
            payload,
            signature,
            'your_webhook_secret'
        )

        if event.type == 'payment.created':
            # Payment initiated
            pass
        elif event.type == 'payment.paid':
            # Payment received (but not confirmed)
            pass
        elif event.type == 'payment.completed':
            # Payment confirmed and completed
            fulfill_order(event.data.payment)
        elif event.type == 'payment.failed':
            # Payment failed
            notify_customer(event.data.payment)
        elif event.type == 'payment.expired':
            # Payment expired
            cleanup_order(event.data.payment)

        return {'status': 'success'}, 200

    except sbtc_gateway.ValidationError:
        return {'error': 'Invalid signature'}, 400

def fulfill_order(payment):
    print(f'Fulfilling order for payment: {payment.id}')

def notify_customer(payment):
    print(f'Notifying customer about failed payment: {payment.id}')

def cleanup_order(payment):
    print(f'Cleaning up expired payment: {payment.id}')
```

## Testing

Use test API keys for development:

```python
# Test API key (starts with sk_test_)
client = sbtc_gateway.SBTCGateway('sk_test_your_test_key_here')

# All payments will use Bitcoin testnet and Stacks testnet
payment = client.payments.create(sbtc_gateway.PaymentRequest(
    amount=10000,  # 0.0001 BTC
    currency='sbtc',
    description='Test payment'
))
```

## Environment Variables

Create a `.env` file:

```bash
# Production
SBTC_API_KEY=sk_live_your_live_key_here
SBTC_WEBHOOK_SECRET=whsec_your_webhook_secret

# Development
SBTC_API_KEY=sk_test_your_test_key_here
SBTC_WEBHOOK_SECRET=whsec_your_test_webhook_secret
```

Use with python-dotenv:

```python
import os
from dotenv import load_dotenv
import sbtc_gateway

load_dotenv()

client = sbtc_gateway.SBTCGateway(os.getenv('SBTC_API_KEY'))
```

## Django Integration

```python
# settings.py
SBTC_API_KEY = os.getenv('SBTC_API_KEY')
SBTC_WEBHOOK_SECRET = os.getenv('SBTC_WEBHOOK_SECRET')

# views.py
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import sbtc_gateway

client = sbtc_gateway.SBTCGateway(settings.SBTC_API_KEY)

@csrf_exempt
@require_http_methods(["POST"])
def webhook_handler(request):
    signature = request.META.get('HTTP_X_SBTC_SIGNATURE')
    payload = request.body.decode('utf-8')

    try:
        event = sbtc_gateway.WebhookUtils.verify_and_parse_event(
            payload, signature, settings.SBTC_WEBHOOK_SECRET
        )

        # Handle the event
        handle_payment_event(event)

        return JsonResponse({'status': 'success'})
    except sbtc_gateway.ValidationError:
        return JsonResponse({'error': 'Invalid signature'}, status=400)
```

## FastAPI Integration

```python
from fastapi import FastAPI, HTTPException, Header, Request
import sbtc_gateway

app = FastAPI()
client = sbtc_gateway.SBTCGateway('sk_live_your_api_key_here')

@app.post("/webhooks/sbtc")
async def webhook_handler(
    request: Request,
    x_sbtc_signature: str = Header(None)
):
    payload = await request.body()

    try:
        event = sbtc_gateway.WebhookUtils.verify_and_parse_event(
            payload.decode('utf-8'),
            x_sbtc_signature,
            'your_webhook_secret'
        )

        # Handle the event
        await handle_payment_event(event)

        return {"status": "success"}
    except sbtc_gateway.ValidationError:
        raise HTTPException(status_code=400, detail="Invalid signature")
```

## Support

- **Documentation**: https://docs.sbtc-gateway.com
- **API Reference**: https://docs.sbtc-gateway.com/api
- **GitHub Issues**: https://github.com/TheSoftNode/sbtc-payment-gateway/issues
- **Email Support**: developers@sbtc-gateway.com

## License

MIT License. See [LICENSE](LICENSE) for details.
