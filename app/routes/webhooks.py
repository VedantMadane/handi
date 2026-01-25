from fastapi import APIRouter, Request, HTTPException
import stripe
import logging
from app.config import STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET

router = APIRouter(prefix="/webhooks", tags=["webhooks"])

stripe.api_key = STRIPE_SECRET_KEY

# Configure logging
logger = logging.getLogger("webhooks")
logging.basicConfig(level=logging.INFO)

@router.post("/stripe")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        logger.error("Invalid payload")
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        logger.error("Invalid signature")
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Handle the event
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        logger.info(f"Payment succeeded: {payment_intent['id']}")
        # TODO: Update DB status to 'success'

    return {"status": "success"}

@router.post("/paypal")
async def paypal_webhook(request: Request):
    # PayPal verification is more complex involving verifying cert chain
    # For this skeleton, we will just accept the post and log it.
    try:
        data = await request.json()
        event_type = data.get("event_type")

        if event_type == "CHECKOUT.ORDER.APPROVED":
            logger.info(f"PayPal Order Approved: {data.get('resource', {}).get('id')}")
            # TODO: Handle approval

        return {"status": "received"}
    except Exception as e:
        logger.error(f"Error processing PayPal webhook: {e}")
        raise HTTPException(status_code=400, detail="Error processing webhook")
