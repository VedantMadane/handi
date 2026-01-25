import asyncio
from paypalcheckoutsdk.core import PayPalHttpClient, SandboxEnvironment
from paypalcheckoutsdk.orders import OrdersCreateRequest, OrdersCaptureRequest
from typing import Dict, Any
from app.config import PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET
from app.payment_providers.base import PaymentProvider

class PayPalProvider(PaymentProvider):
    def __init__(self):
        # Default to Sandbox for MVP
        self.environment = SandboxEnvironment(client_id=PAYPAL_CLIENT_ID, client_secret=PAYPAL_CLIENT_SECRET)
        self.client = PayPalHttpClient(self.environment)

    async def create_order(self, amount: float, currency: str) -> Dict[str, Any]:
        request = OrdersCreateRequest()
        request.prefer('return=representation')
        request.request_body({
            "intent": "CAPTURE",
            "purchase_units": [
                {
                    "amount": {
                        "currency_code": currency,
                        "value": str(amount)
                    }
                }
            ]
        })

        try:
            # Sync call moved to executor
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, lambda: self.client.execute(request))
            return {
                "provider": "paypal",
                "order_id": response.result.id,
                "status": response.result.status
            }
        except Exception as e:
             raise ValueError(f"PayPal Create Order Failed: {str(e)}")


    async def verify_payment(self, data: Dict[str, Any]) -> Dict[str, Any]:
        order_id = data.get("paypal_order_id")
        if not order_id:
             raise ValueError("Missing paypal_order_id")

        request = OrdersCaptureRequest(order_id)

        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, lambda: self.client.execute(request))

            # Check for COMPLETED status
            if response.result.status == "COMPLETED":
                 # Usually result.purchase_units[0].payments.captures[0].id is the transaction id
                 # Using safe access if possible, simplified for MVP
                 capture_id = response.result.purchase_units[0].payments.captures[0].id
                 return {
                     "transaction_id": capture_id,
                     "status": "success"
                 }
            else:
                 raise ValueError(f"PayPal Capture Failed: Status is {response.result.status}")
        except Exception as e:
             raise ValueError(f"PayPal Capture Failed: {str(e)}")
