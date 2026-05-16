"""
Payment Service - Core payment processing logic
"""
from typing import Dict, Optional
from .models import Payment, PaymentStatus
from .events import PaymentProcessedEvent, emit_event
from .analytics import track_payment


class PaymentService:
    """Handles payment processing and status management."""
    
    def __init__(self, payment_gateway):
        self.gateway = payment_gateway
    
    def process_payment(self, payment: Payment) -> Dict:
        """
        Process a payment through the gateway.
        
        Args:
            payment: Payment object with amount and details
            
        Returns:
            Dict with processing result
        """
        # Validate payment
        if not self._validate_payment(payment):
            return {"status": "INVALID", "error": "Invalid payment data"}
        
        # Process through gateway
        result = self.gateway.charge(payment.amount, payment.card_token)
        
        if result["success"]:
            # Update payment status
            payment.status = PaymentStatus.PENDING  # This will change to PROCESSING
            payment.transaction_id = result["transaction_id"]
            
            # Emit event for downstream services
            event = PaymentProcessedEvent(
                payment_id=payment.id,
                amount=payment.amount,
                status=payment.status,
                transaction_id=payment.transaction_id
            )
            emit_event(event)
            
            # Track for analytics
            track_payment(payment)
            
            return {"status": "SUCCESS", "payment_id": payment.id}
        else:
            payment.status = PaymentStatus.FAILED
            return {"status": "FAILED", "error": result["error"]}
    
    def _validate_payment(self, payment: Payment) -> bool:
        """Validate payment data before processing."""
        return (
            payment.amount > 0 and
            payment.card_token is not None and
            len(payment.card_token) > 0
        )
    
    def get_payment_status(self, payment_id: str) -> Optional[str]:
        """Get current status of a payment."""
        # This would query the database
        return PaymentStatus.PENDING

# Made with Bob
