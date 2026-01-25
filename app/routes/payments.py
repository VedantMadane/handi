from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services import create_donation
from app.payment_providers.factory import get_payment_provider

router = APIRouter()

class OrderRequest(BaseModel):
    amount: float
    currency: str = "INR"
    provider: str = "razorpay"

class PaymentVerify(BaseModel):
    provider: str
    amount: float
    currency: str
    purpose: str
    payment_data: Dict[str, Any]

@router.post("/donations/create_order")
async def create_order(data: OrderRequest):
    try:
        provider = get_payment_provider(data.provider)
        order_details = await provider.create_order(data.amount, data.currency)
        return order_details
    except ValueError as e:
         raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/donations/verify")
async def verify_payment(data: PaymentVerify, db: AsyncSession = Depends(get_db)):
    try:
        provider = get_payment_provider(data.provider)
        # Verify specific to the provider
        verification_result = await provider.verify_payment(data.payment_data)

        # If successful (no exception raised), record donation
        # For MVP, assume Guest User (ID 1)
        donor_id = 1

        donation = await create_donation(
            db=db,
            amount=data.amount,
            currency=data.currency,
            donor_id=donor_id,
            purpose=data.purpose,
            payment_gateway=data.provider,
            transaction_id=verification_result["transaction_id"]
        )

        return {"status": "success", "donation_hash": donation.record_hash}

    except Exception as e:
        # Log error here ideally
        raise HTTPException(status_code=400, detail=str(e))
