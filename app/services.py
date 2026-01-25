import hashlib
from datetime import datetime
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Donation, User

async def calculate_donation_hash(prev_hash: str, amount: float, currency: str, donor_id: int, timestamp: datetime, purpose: str) -> str:
    # Normalize timestamp to string
    ts_str = timestamp.isoformat()
    # Added currency to the hash input
    data = f"{prev_hash}{amount}{currency}{donor_id}{ts_str}{purpose}"
    return hashlib.sha256(data.encode()).hexdigest()

async def create_donation(db: AsyncSession, amount: float, donor_id: int, purpose: str, currency: str = "USD", note: str = None) -> Donation:
    # 1. Get the latest donation to find the previous hash
    # Order by ID desc to get the last one
    stmt = select(Donation).order_by(desc(Donation.id)).limit(1)
    result = await db.execute(stmt)
    last_donation = result.scalars().first()

    if last_donation:
        prev_hash = last_donation.record_hash
    else:
        # Genesis hash (all zeros)
        prev_hash = "0" * 64

    timestamp = datetime.utcnow()

    # 2. Calculate new hash (Now includes currency)
    record_hash = await calculate_donation_hash(prev_hash, amount, currency, donor_id, timestamp, purpose)

    # 3. Create record
    new_donation = Donation(
        amount=amount,
        currency=currency,
        donor_id=donor_id,
        purpose=purpose,
        note=note,
        timestamp=timestamp,
        previous_hash=prev_hash,
        record_hash=record_hash
    )

    db.add(new_donation)
    await db.commit()
    await db.refresh(new_donation)

    return new_donation
