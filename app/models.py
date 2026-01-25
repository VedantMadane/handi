import enum
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Integer, DateTime, ForeignKey, Float, Enum, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    PRIEST = "priest"
    DEVOTEE = "devotee"

class StaffRole(str, enum.Enum):
    SECURITY = "security"
    CLEANING = "cleaning"
    MANAGEMENT = "management"
    PRIEST = "priest"
    VOLUNTEER = "volunteer"

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String, unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String)
    email: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    password_hash: Mapped[str] = mapped_column(String)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.DEVOTEE)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    donations: Mapped[List["Donation"]] = relationship(back_populates="donor")
    attendances: Mapped[List["Attendance"]] = relationship(back_populates="user")
    staff_profile: Mapped[Optional["Staff"]] = relationship(back_populates="user", uselist=False)


class Donation(Base):
    __tablename__ = "donations"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    amount: Mapped[float] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String, default="USD")
    donor_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    purpose: Mapped[str] = mapped_column(String) # e.g., "General", "Annadhanam", "Building Fund"
    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Immutable Ledger Fields
    previous_hash: Mapped[str] = mapped_column(String) # Hash of the previous record
    record_hash: Mapped[str] = mapped_column(String, unique=True) # Hash of this record (including prev_hash)

    donor: Mapped["User"] = relationship(back_populates="donations")


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String)
    description: Mapped[Optional[str]] = mapped_column(Text)
    location: Mapped[str] = mapped_column(String)
    start_time: Mapped[datetime] = mapped_column(DateTime)
    end_time: Mapped[datetime] = mapped_column(DateTime)
    capacity: Mapped[int] = mapped_column(Integer)

    attendees: Mapped[List["Attendance"]] = relationship(back_populates="event")


class Attendance(Base):
    __tablename__ = "attendance"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    status: Mapped[str] = mapped_column(String, default="registered") # registered, attended, cancelled
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    event: Mapped["Event"] = relationship(back_populates="attendees")
    user: Mapped["User"] = relationship(back_populates="attendances")


class Staff(Base):
    __tablename__ = "staff"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    role: Mapped[StaffRole] = mapped_column(Enum(StaffRole))
    notes: Mapped[Optional[str]] = mapped_column(Text)

    user: Mapped["User"] = relationship(back_populates="staff_profile")
    shifts: Mapped[List["Shift"]] = relationship(back_populates="staff_member")


class Shift(Base):
    __tablename__ = "shifts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    staff_id: Mapped[int] = mapped_column(ForeignKey("staff.id"))
    start_time: Mapped[datetime] = mapped_column(DateTime)
    end_time: Mapped[datetime] = mapped_column(DateTime)
    location: Mapped[str] = mapped_column(String) # e.g., "Main Gate", "Sanctum", "Kitchen"

    staff_member: Mapped["Staff"] = relationship(back_populates="shifts")
