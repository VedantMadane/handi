import asyncio
import stripe
from typing import Dict, Any
from app.config import STRIPE_SECRET_KEY, STRIPE_PUBLISHABLE_KEY
from app.payment_providers.base import PaymentProvider

class StripeProvider(PaymentProvider):
    def __init__(self):
        stripe.api_key = STRIPE_SECRET_KEY

    async def create_order(self, amount: float, currency: str) -> Dict[str, Any]:
        amount_cents = int(amount * 100)

        loop = asyncio.get_event_loop()
        intent = await loop.run_in_executor(None, lambda: stripe.PaymentIntent.create(
            amount=amount_cents,
            currency=currency.lower(),
            automatic_payment_methods={"enabled": True},
        ))

        return {
            "provider": "stripe",
            "client_secret": intent.client_secret,
            "publishable_key": STRIPE_PUBLISHABLE_KEY,
            "payment_intent_id": intent.id
        }

    async def verify_payment(self, data: Dict[str, Any]) -> Dict[str, Any]:
        payment_intent_id = data.get("payment_intent_id")

        if not payment_intent_id:
            raise ValueError("Missing payment_intent_id")

        loop = asyncio.get_event_loop()
        intent = await loop.run_in_executor(None, lambda: stripe.PaymentIntent.retrieve(payment_intent_id))

        if intent.status == "succeeded":
            return {
                "transaction_id": intent.id,
                "status": "success"
            }
        else:
             raise ValueError(f"Payment verification failed: Status is {intent.status}")
