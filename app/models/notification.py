import enum
from datetime import datetime
from sqlalchemy import String, DateTime, Enum, Integer, ForeignKey, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class NotificationStatus(str, enum.Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    CANCELLED = "cancelled"


class NotificationType(str, enum.Enum):
    BREAK_REMINDER = "break_reminder"
    BREAK_OVERDUE = "break_overdue"
    CONSTRAINT_REMINDER = "constraint_reminder"
    SHIFT_PUBLISHED = "shift_published"
    SWAP_REQUEST = "swap_request"
    SWAP_APPROVED = "swap_approved"
    TASK_ASSIGNED = "task_assigned"
    CHECKLIST_REMINDER = "checklist_reminder"
    OTP = "otp"
    GENERAL = "general"


class NotificationQueue(Base):
    __tablename__ = "notification_queue"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    notification_type: Mapped[NotificationType] = mapped_column(Enum(NotificationType), nullable=False)
    template_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    message_body: Mapped[str] = mapped_column(Text, nullable=False)
    payload_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[NotificationStatus] = mapped_column(Enum(NotificationStatus), default=NotificationStatus.PENDING)
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    unique_key: Mapped[str | None] = mapped_column(String(120), unique=True, nullable=True)  # prevent duplicates
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
