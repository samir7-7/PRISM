"""
Data models for payment system
"""
from enum import Enum
from dataclasses import dataclass
from typing import Optional


class PaymentStatus(Enum):
    """Payment status enumeration."""
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


@dataclass
class Payment:
    """Payment data model."""
    id: str
    amount: float
    card_token: str
    status: PaymentStatus
    transaction_id: Optional[str] = None
    customer_id: Optional[str] = None

# Made with Bob
