import unittest
from unittest.mock import MagicMock, patch
import asyncio
from app.main import app
from app.database import Base, get_db
from app.models import User, Event, Attendance
from starlette.testclient import TestClient
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool
from sqlalchemy import select

# Setup test DB engine
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False, poolclass=StaticPool)
TestAsyncSessionLocal = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)

async def override_get_db():
    async with TestAsyncSessionLocal() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db

# TestClient
client = TestClient(app)

class TestViews(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Initialize DB and create a user
        async def init_data():
            async with test_engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)
                await conn.run_sync(Base.metadata.create_all)

            # Create a user with ID 1
            async with test_engine.connect() as conn:
                await conn.execute(
                    User.__table__.insert().values(
                        id=1, username="testuser", full_name="Test User", email="test@handi.com", password_hash="hashed_secret", role="DEVOTEE"
                    )
                )
                # Create an event
                await conn.execute(
                    Event.__table__.insert().values(
                        id=1, title="Test Event", location="Test Location", start_time=datetime.now(timezone.utc), end_time=datetime.now(timezone.utc), capacity=100
                    )
                )
                await conn.commit()

        asyncio.run(init_data())

    @classmethod
    def tearDownClass(cls):
        # Clean up dependency override
        app.dependency_overrides = {}

    def test_rsvp(self):
        # First RSVP
        response = client.post("/events/1/rsvp")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Registered", response.text)

        # Second RSVP (should be already registered)
        response = client.post("/events/1/rsvp")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Already Registered", response.text)

if __name__ == '__main__':
    unittest.main()
