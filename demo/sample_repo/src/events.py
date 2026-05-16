"""
Event system for payment processing
"""
from dataclasses import dataclass
from typing import Any


@dataclass
class PaymentProcessedEvent:
    """Event emitted when a payment is processed."""
    payment_id: str
    amount: float
    status: Any  # PaymentStatus enum
    transaction_id: str


def emit_event(event: PaymentProcessedEvent) -> None:
    """
    Emit an event to the event bus.
    This would typically publish to a message queue.
    """
    # In a real system, this would publish to Kafka, RabbitMQ, etc.
    print(f"Event emitted: {event}")

# Made with Bob
