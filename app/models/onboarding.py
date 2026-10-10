from datetime import datetime
from sqlalchemy import String, DateTime, Integer, ForeignKey, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class OnboardingTemplate(Base):
    __tablename__ = "onboarding_templates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    day_number: Mapped[int] = mapped_column(Integer, nullable=False)  # 1, 2, 3...
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    requires_upload: Mapped[bool] = mapped_column(Boolean, default=False)
    requires_signature: Mapped[bool] = mapped_column(Boolean, default=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class OnboardingProgress(Base):
    __tablename__ = "onboarding_progress"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    template_id: Mapped[int] = mapped_column(ForeignKey("onboarding_templates.id"), nullable=False)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    file_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    signature_data: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
