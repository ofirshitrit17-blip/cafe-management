from datetime import datetime, date
from sqlalchemy import String, DateTime, Date, Integer, ForeignKey, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class TaskTemplate(Base):
    __tablename__ = "task_templates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    requires_photo: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class DailyTaskAssignment(Base):
    __tablename__ = "daily_task_assignments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    task_template_id: Mapped[int] = mapped_column(ForeignKey("task_templates.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    assignment_date: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    photo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
