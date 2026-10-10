import enum
from datetime import datetime, date, time
from sqlalchemy import String, DateTime, Date, Time, Enum, Integer, ForeignKey, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class SwapStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED_BY_EMPLOYEE = "accepted_by_employee"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class Shift(Base):
    __tablename__ = "shifts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    shift_date: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    role_in_shift: Mapped[str | None] = mapped_column(String(50), nullable=True)  # barista / cashier / etc
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="shifts")


class ShiftConstraint(Base):
    __tablename__ = "shift_constraints"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    week_start: Mapped[date] = mapped_column(Date, index=True, nullable=False)  # Monday of the week
    unavailable_dates: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON list of dates
    preferred_shifts: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    is_late_submission: Mapped[bool] = mapped_column(Boolean, default=False)

    user = relationship("User", back_populates="constraints")


class ShiftSwapRequest(Base):
    __tablename__ = "shift_swap_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    requester_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    target_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    original_shift_id: Mapped[int] = mapped_column(ForeignKey("shifts.id"), nullable=False)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[SwapStatus] = mapped_column(Enum(SwapStatus), default=SwapStatus.PENDING)
    manager_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    manager_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
