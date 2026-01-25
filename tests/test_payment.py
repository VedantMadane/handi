import unittest
from unittest.mock import MagicMock, patch
import asyncio
from app.main import app
from app.database import engine, Base
from app.models import User
from starlette.testclient import TestClient

# TestClient
client = TestClient(app)

class TestPayment(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Initialize DB and create a user
        async def init_data():
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)
                await conn.run_sync(Base.metadata.create_all)

            # Create a user with ID 1
            async with engine.connect() as conn:
                await conn.execute(
                    User.__table__.insert().values(
                        id=1, username="admin", full_name="Admin User", email="admin@handi.com", password_hash="hashed_secret", role="ADMIN"
                    )
                )
                await conn.commit()

        asyncio.run(init_data())

    def test_create_order(self):
        with patch('app.payment_providers.razorpay_provider.razorpay.Client') as MockClient:
            mock_instance = MockClient.return_value
            mock_instance.order.create.return_value = {
                "id": "order_test_123",
                "amount": 50000,
                "currency": "INR",
                "key_id": "test_key"
            }

            response = client.post("/donations/create_order", json={
                "amount": 500.0,
                "currency": "INR",
                "provider": "razorpay"
            })

            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["order_id"], "order_test_123")
            self.assertEqual(data["amount"], 50000)

    def test_verify_payment(self):
        with patch('app.payment_providers.razorpay_provider.razorpay.Client') as MockClient:
            mock_instance = MockClient.return_value
            # Mock utility.verify_payment_signature to return None (success)
            mock_instance.utility.verify_payment_signature.return_value = None

            payload = {
                "provider": "razorpay",
                "amount": 500.0,
                "currency": "INR",
                "purpose": "General Fund",
                "payment_data": {
                    "razorpay_payment_id": "pay_test_456",
                    "razorpay_order_id": "order_test_123",
                    "razorpay_signature": "sig_test_789"
                }
            }

            response = client.post("/donations/verify", json=payload)

            if response.status_code != 200:
                print(response.json())

            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["status"], "success")
            self.assertTrue("donation_hash" in data)

    def test_create_order_stripe(self):
        with patch('app.payment_providers.stripe_provider.stripe.PaymentIntent') as MockIntent:
            MockIntent.create.return_value = MagicMock(
                client_secret="secret_123",
                id="pi_123"
            )

            response = client.post("/donations/create_order", json={
                "amount": 50.0,
                "currency": "INR",
                "provider": "stripe"
            })

            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["provider"], "stripe")
            self.assertEqual(data["payment_intent_id"], "pi_123")

    def test_verify_payment_stripe(self):
         with patch('app.payment_providers.stripe_provider.stripe.PaymentIntent') as MockIntent:
            MockIntent.retrieve.return_value = MagicMock(
                status="succeeded",
                id="pi_123"
            )

            payload = {
                "provider": "stripe",
                "amount": 50.0,
                "currency": "INR",
                "purpose": "General Fund",
                "payment_data": {
                    "payment_intent_id": "pi_123"
                }
            }

            response = client.post("/donations/verify", json=payload)
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["status"], "success")

    def test_create_order_paypal(self):
        with patch('app.payment_providers.paypal_provider.PayPalHttpClient') as MockClient:
            mock_instance = MockClient.return_value
            mock_response = MagicMock()
            mock_response.result.id = "order_paypal_123"
            mock_response.result.status = "CREATED"
            mock_instance.execute.return_value = mock_response

            response = client.post("/donations/create_order", json={
                "amount": 50.0,
                "currency": "INR",
                "provider": "paypal"
            })

            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["provider"], "paypal")
            self.assertEqual(data["order_id"], "order_paypal_123")

    def test_verify_payment_paypal(self):
         with patch('app.payment_providers.paypal_provider.PayPalHttpClient') as MockClient:
            mock_instance = MockClient.return_value
            mock_response = MagicMock()
            mock_response.result.status = "COMPLETED"
            mock_response.result.purchase_units = [
                MagicMock(payments=MagicMock(captures=[MagicMock(id="capture_123")]))
            ]
            mock_instance.execute.return_value = mock_response

            payload = {
                "provider": "paypal",
                "amount": 50.0,
                "currency": "INR",
                "purpose": "General Fund",
                "payment_data": {
                    "paypal_order_id": "order_paypal_123"
                }
            }

            response = client.post("/donations/verify", json=payload)
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["status"], "success")

if __name__ == '__main__':
    unittest.main()
