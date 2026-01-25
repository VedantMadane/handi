import unittest
from unittest.mock import MagicMock, patch
import asyncio
from app.main import app
from app.database import engine, Base
from app.models import User
from starlette.testclient import TestClient
from sqlalchemy.future import select

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

            # Create a user with ID 1 (required by the hardcoded logic in verify_payment)
            async with engine.connect() as conn:
                # We can't easily use ORM with connect() directly for simple insertion unless we set up a session
                # But we can use raw SQL or just use a session.
                # Let's use the startup event or just insert manually if we had a session.
                # Easiest is to use the app's db dependency logic or just raw insert.
                await conn.execute(
                    User.__table__.insert().values(
                        id=1, username="admin", full_name="Admin User", email="admin@handi.com", password_hash="hashed_secret", role="ADMIN"
                    )
                )
                await conn.commit()

        asyncio.run(init_data())

    def test_create_order(self):
        with patch('app.routes.payments.client') as mock_client:
            mock_client.order.create.return_value = {
                "id": "order_test_123",
                "amount": 50000,
                "currency": "INR",
                "key_id": "test_key"
            }

            response = client.post("/donations/create_order", json={
                "amount": 500.0,
                "currency": "INR"
            })

            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["id"], "order_test_123")
            self.assertEqual(data["amount"], 50000)

    def test_verify_payment(self):
        with patch('app.routes.payments.client') as mock_client:
            # Mock utility.verify_payment_signature to return None (success)
            mock_client.utility.verify_payment_signature.return_value = None

            payload = {
                "razorpay_payment_id": "pay_test_456",
                "razorpay_order_id": "order_test_123",
                "razorpay_signature": "sig_test_789",
                "amount": 500.0,
                "currency": "INR",
                "purpose": "General Fund"
            }

            response = client.post("/donations/verify", json=payload)

            if response.status_code != 200:
                print(response.json())

            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["status"], "success")
            self.assertTrue("donation_hash" in data)

if __name__ == '__main__':
    unittest.main()
