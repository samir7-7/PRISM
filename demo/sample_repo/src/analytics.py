"""
Analytics tracking for payment events
"""
from typing import Any


def track_payment(payment: Any) -> None:
    """
    Track payment for analytics.
    This service expects PENDING status for new payments.
    
    Args:
        payment: Payment object to track
    """
    # Analytics service expects the old PENDING status
    # If this changes to PROCESSING, analytics will break
    print(f"Tracking payment {payment.id} with status {payment.status}")
    
    # Send to analytics platform
    _send_to_analytics({
        "event": "payment_processed",
        "payment_id": payment.id,
        "amount": payment.amount,
        "status": payment.status
    })


def _send_to_analytics(data: dict) -> None:
    """Send data to analytics platform."""
    # In a real system, this would send to Mixpanel, Segment, etc.
    pass

# Made with Bob
