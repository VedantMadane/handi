import unittest
from unittest.mock import MagicMock, patch
from starlette.testclient import TestClient
from app.main import app
import stripe

client = TestClient(app)

class TestWebhooks(unittest.TestCase):

    @patch('app.routes.webhooks.stripe.Webhook.construct_event')
    def test_stripe_webhook_success(self, mock_construct_event):
        # Mock successful event construction
        mock_construct_event.return_value = {
            'type': 'payment_intent.succeeded',
            'data': {
                'object': {
                    'id': 'pi_12345'
                }
            }
        }

        response = client.post(
            "/webhooks/stripe",
            json={"data": "test"},
            headers={"stripe-signature": "valid_sig"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "success"})

    @patch('app.routes.webhooks.stripe.Webhook.construct_event')
    def test_stripe_webhook_invalid_signature(self, mock_construct_event):
        # Mock signature error
        mock_construct_event.side_effect = stripe.error.SignatureVerificationError("Invalid sig", "sig_header")

        response = client.post(
            "/webhooks/stripe",
            json={"data": "test"},
            headers={"stripe-signature": "invalid_sig"}
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"detail": "Invalid signature"})

    def test_paypal_webhook(self):
        # PayPal webhook just logs and returns 200 for now
        response = client.post(
            "/webhooks/paypal",
            json={"event_type": "CHECKOUT.ORDER.APPROVED", "resource": {"id": "order_123"}}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "received"})

if __name__ == '__main__':
    unittest.main()
