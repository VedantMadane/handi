import strawberry
from typing import List, Optional
from datetime import datetime
from strawberry.types import Info
from sqlalchemy import select
from app.models import User, Donation, Event, Staff, Attendance, StaffRole, UserRole
from app.database import get_db

# --- Types ---

@strawberry.type
class UserType:
    id: int
    username: str
    full_name: str
    role: str

@strawberry.type
class DonationType:
    id: int
    amount: float
    currency: str
    purpose: str
    note: Optional[str]
    timestamp: datetime
    previous_hash: str
    record_hash: str
    donor_id: int

@strawberry.type
class EventType:
    id: int
    title: str
    description: Optional[str]
    location: str
    start_time: datetime
    end_time: datetime
    capacity: int

@strawberry.type
class StaffType:
    id: int
    role: str
    notes: Optional[str]
    user: UserType

# --- Queries ---

@strawberry.type
class Query:
    @strawberry.field
    async def users(self, info: Info, limit: int = 100, offset: int = 0) -> List[UserType]:
        db = info.context["db"]
        result = await db.execute(select(User).limit(limit).offset(offset))
        users = result.scalars().all()
        return [
            UserType(
                id=u.id,
                username=u.username,
                full_name=u.full_name,
                role=u.role.value
            ) for u in users
        ]

    @strawberry.field
    async def donations(self, info: Info) -> List[DonationType]:
        db = info.context["db"]
        # Public ledger: maybe limit or paginate in real life
        result = await db.execute(select(Donation).order_by(Donation.id))
        donations = result.scalars().all()
        return [
            DonationType(
                id=d.id,
                amount=d.amount,
                currency=d.currency,
                purpose=d.purpose,
                note=d.note,
                timestamp=d.timestamp,
                previous_hash=d.previous_hash,
                record_hash=d.record_hash,
                donor_id=d.donor_id
            ) for d in donations
        ]

    @strawberry.field
    async def events(self, info: Info) -> List[EventType]:
        db = info.context["db"]
        result = await db.execute(select(Event))
        events = result.scalars().all()
        return [
            EventType(
                id=e.id,
                title=e.title,
                description=e.description,
                location=e.location,
                start_time=e.start_time,
                end_time=e.end_time,
                capacity=e.capacity
            ) for e in events
        ]

    @strawberry.field
    async def staff(self, info: Info) -> List[StaffType]:
        db = info.context["db"]
        from sqlalchemy.orm import selectinload

        result = await db.execute(select(Staff).options(selectinload(Staff.user)))
        staff_members = result.scalars().all()

        return [
            StaffType(
                id=s.id,
                role=s.role.value,
                notes=s.notes,
                user=UserType(
                    id=s.user.id,
                    username=s.user.username,
                    full_name=s.user.full_name,
                    role=s.user.role.value
                )
            ) for s in staff_members
        ]

schema = strawberry.Schema(query=Query)
