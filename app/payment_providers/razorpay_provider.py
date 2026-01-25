import razorpay
from typing import Dict, Any
from app.config import RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET
from app.payment_providers.base import PaymentProvider

class RazorpayProvider(PaymentProvider):
    def __init__(self):
        self.client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

    async def create_order(self, amount: float, currency: str) -> Dict[str, Any]:
        amount_paise = int(amount * 100)
        order_data = {
            "amount": amount_paise,
            "currency": currency,
            "payment_capture": 1
        }
        order = self.client.order.create(data=order_data)
        return {
            "provider": "razorpay",
            "order_id": order["id"],
            "amount": order["amount"],
            "currency": order["currency"],
            "key_id": RAZORPAY_KEY_ID
        }

    async def verify_payment(self, data: Dict[str, Any]) -> Dict[str, Any]:
        params_dict = {
            'razorpay_order_id': data.get('razorpay_order_id'),
            'razorpay_payment_id': data.get('razorpay_payment_id'),
            'razorpay_signature': data.get('razorpay_signature')
        }

        # Verify signature - raises error if invalid
        self.client.utility.verify_payment_signature(params_dict)

        return {
            "transaction_id": data.get('razorpay_payment_id'),
            "status": "success"
        }
