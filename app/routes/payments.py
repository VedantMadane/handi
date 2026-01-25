import razorpay
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.config import RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET
from app.services import create_donation
from app.models import User

router = APIRouter()
client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

class OrderRequest(BaseModel):
    amount: float
    currency: str = "INR"

class PaymentVerify(BaseModel):
    razorpay_payment_id: str
    razorpay_order_id: str
    razorpay_signature: str
    amount: float
    currency: str
    purpose: str

@router.post("/donations/create_order")
async def create_order(request: Request, data: OrderRequest):
    amount_paise = int(data.amount * 100) # Razorpay expects amount in paise

    order_data = {
        "amount": amount_paise,
        "currency": data.currency,
        "payment_capture": 1 # Auto capture
    }

    try:
        order = client.order.create(data=order_data)
        return {
            "id": order["id"],
            "amount": order["amount"],
            "currency": order["currency"],
            "key_id": RAZORPAY_KEY_ID
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/donations/verify")
async def verify_payment(data: PaymentVerify, db: AsyncSession = Depends(get_db)):
    # 1. Verify Signature
    params_dict = {
        'razorpay_order_id': data.razorpay_order_id,
        'razorpay_payment_id': data.razorpay_payment_id,
        'razorpay_signature': data.razorpay_signature
    }

    try:
        client.utility.verify_payment_signature(params_dict)
    except razorpay.errors.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid Payment Signature")

    # 2. Add to Immutable Ledger
    # For MVP, assume Guest User (ID 1) or derived from Auth if logged in
    # Ideally, we get user_id from Depends(get_current_user)
    # Using ID 1 (Admin) as placeholder if not logged in
    donor_id = 1

    donation = await create_donation(
        db=db,
        amount=data.amount,
        currency=data.currency,
        donor_id=donor_id,
        purpose=data.purpose,
        payment_gateway="razorpay",
        transaction_id=data.razorpay_payment_id
    )

    return {"status": "success", "donation_hash": donation.record_hash}
