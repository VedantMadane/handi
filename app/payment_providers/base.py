from abc import ABC, abstractmethod
from typing import Dict, Any

class PaymentProvider(ABC):
    @abstractmethod
    async def create_order(self, amount: float, currency: str) -> Dict[str, Any]:
        """Creates an order/intent on the payment gateway."""
        pass

    @abstractmethod
    async def verify_payment(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Verifies the payment with the gateway. Returns transaction details."""
        pass
