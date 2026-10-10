import enum
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Enum, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class UserRole(str, enum.Enum):
    EMPLOYEE = "employee"
    SHIFT_MANAGER = "shift_manager"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    phone: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.EMPLOYEE, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_onboarding_complete: Mapped[bool] = mapped_column(Boolean, default=False)
    hired_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    attendance_events = relationship("AttendanceEvent", back_populates="user", lazy="selectin")
    break_sessions = relationship("BreakSession", back_populates="user", lazy="selectin")
    shifts = relationship("Shift", back_populates="user", lazy="selectin")
    constraints = relationship("ShiftConstraint", back_populates="user", lazy="selectin")

    def __repr__(self) -> str:
        return f"<User {self.full_name} ({self.phone})>"
