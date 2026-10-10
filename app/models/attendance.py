import enum
from datetime import datetime
from sqlalchemy import String, DateTime, Enum, Integer, ForeignKey, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class AttendanceEventType(str, enum.Enum):
    CLOCK_IN = "clock_in"
    CLOCK_OUT = "clock_out"
    MANUAL_CORRECTION = "manual_correction"


class AttendanceEvent(Base):
    __tablename__ = "attendance_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    event_type: Mapped[AttendanceEventType] = mapped_column(Enum(AttendanceEventType), nullable=False)
    event_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)  # server time
    source: Mapped[str] = mapped_column(String(50), default="mobile")  # mobile / tablet_qr / manual
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    is_late: Mapped[bool] = mapped_column(Boolean, default=False)
    correction_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    corrected_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    user = relationship("User", back_populates="attendance_events", foreign_keys=[user_id])

    def __repr__(self) -> str:
        return f"<Attendance {self.event_type} user={self.user_id} at={self.event_time}>"
