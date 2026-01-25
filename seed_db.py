import asyncio
from app.database import init_db, AsyncSessionLocal
from app.models import Event, Donation, User, UserRole
from app.services import create_donation
from datetime import datetime, timedelta

from sqlalchemy import select

async def seed():
    print("Initializing database...")
    await init_db()
    async with AsyncSessionLocal() as session:
        # Check if Admin User exists
        result = await session.execute(select(User).where(User.username == "admin"))
        if result.scalars().first():
            print("Database already seeded. Skipping.")
            return

        # Create Admin User
        user = User(username="admin", full_name="Admin User", password_hash="hash", role=UserRole.ADMIN)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        print(f"Created user: {user.username}")

        # Create Event
        event = Event(
            title="Maha Shivaratri",
            description="Night of Shiva",
            location="Main Hall",
            start_time=datetime.now() + timedelta(days=1),
            end_time=datetime.now() + timedelta(days=1, hours=4),
            capacity=100
        )
        session.add(event)
        print(f"Created event: {event.title}")

        # Create Donations (This triggers the hash chain logic)
        await create_donation(session, 1001.0, user.id, "Temple Renovation", currency="USD")
        await create_donation(session, 501.0, user.id, "Annadhanam", currency="INR")
        await create_donation(session, 101.0, user.id, "General Fund", currency="EUR")

        await session.commit()
        print("Database seeded successfully with Users, Events, and hashed Donations.")

if __name__ == "__main__":
    asyncio.run(seed())
