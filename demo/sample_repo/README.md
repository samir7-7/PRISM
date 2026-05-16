# Payment Service Demo Repository

This is a sample repository demonstrating a payment processing service with multiple interconnected components.

## Structure

```
src/
├── payment_service.py  # Core payment processing logic
├── models.py          # Data models (Payment, PaymentStatus enum)
├── events.py          # Event emission system
├── analytics.py       # Analytics tracking
└── __init__.py        # Package exports

tests/
└── test_payment_service.py  # Unit tests
```

## Demo Scenario

This repository demonstrates a semantic risk scenario where:

1. **The Change**: `PaymentStatus.PENDING` is renamed to `PaymentStatus.PROCESSING` in `models.py`
2. **The Risk**: The `analytics.py` service expects `PENDING` status and will break
3. **The Impact**: Analytics tracking fails silently, causing data loss

This is exactly the type of semantic risk that PRISM is designed to detect - a syntactically valid change that breaks downstream assumptions.

## Components

- **PaymentService**: Processes payments and emits events
- **Models**: Defines Payment data structure and status enum
- **Events**: Event bus for inter-service communication  
- **Analytics**: Tracks payment events (depends on PENDING status)