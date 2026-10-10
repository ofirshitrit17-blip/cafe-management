from datetime import timedelta
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.break_session import BreakSession, BreakStatus
from app.models.user import User
from app.models.notification import NotificationType
from app.models.audit import AuditLog
from app.services.notifications import enqueue_notification, cancel_notifications_by_key_prefix
from app.utils.time_utils import utc_now
from app.config import get_settings

settings = get_settings()


async def start_break(
    db: AsyncSession,
    user: User,
    duration_minutes: int | None = None,
    break_type: str = "general",
) -> BreakSession:
    duration = duration_minutes or settings.DEFAULT_BREAK_MINUTES
    now = utc_now()
    planned_end = now + timedelta(minutes=duration)

    # Check no active break
    existing = await db.execute(
        select(BreakSession).where(
            and_(
                BreakSession.user_id == user.id,
                BreakSession.status == BreakStatus.ACTIVE,
            )
        )
    )
    if existing.scalar_one_or_none():
        raise ValueError("כבר יש הפסקה פעילה")

    session = BreakSession(
        user_id=user.id,
        started_at=now,
        planned_end_at=planned_end,
        duration_minutes=duration,
        status=BreakStatus.ACTIVE,
        break_type=break_type,
    )
    db.add(session)
    await db.flush()

    # Schedule one reminder X minutes before end
    reminder_at = planned_end - timedelta(minutes=settings.BREAK_REMINDER_MINUTES_BEFORE)
    if reminder_at > now:
        await enqueue_notification(
            db,
            phone=user.phone,
            notification_type=NotificationType.BREAK_REMINDER,
            message_body=f"היי {user.full_name}, נשארו {settings.BREAK_REMINDER_MINUTES_BEFORE} דקות לסיום ההפסקה. נא לחזור בקרוב.",
            user_id=user.id,
            scheduled_at=reminder_at,
            unique_key=f"break_reminder_{session.id}",
        )

    # Schedule overdue alert to managers (will be picked by worker)
    await enqueue_notification(
        db,
        phone=user.phone,  # will be replaced by manager phones in full version
        notification_type=NotificationType.BREAK_OVERDUE,
        message_body=f"חריגת הפסקה: {user.full_name} עבר את זמן ההפסקה ({duration} דק').",
        user_id=user.id,
        scheduled_at=planned_end + timedelta(seconds=30),
        unique_key=f"break_overdue_{session.id}",
    )

    audit = AuditLog(
        actor_id=user.id,
        action="break_start",
        entity_type="break_session",
        entity_id=session.id,
        details=f"duration={duration}, type={break_type}",
    )
    db.add(audit)
    await db.flush()
    return session


async def end_break(db: AsyncSession, user: User) -> BreakSession:
    result = await db.execute(
        select(BreakSession).where(
            and_(
                BreakSession.user_id == user.id,
                BreakSession.status == BreakStatus.ACTIVE,
            )
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise ValueError("אין הפסקה פעילה")

    session.ended_at = utc_now()
    session.status = BreakStatus.COMPLETED

    # Cancel pending reminder & overdue
    await cancel_notifications_by_key_prefix(db, f"break_reminder_{session.id}")
    await cancel_notifications_by_key_prefix(db, f"break_overdue_{session.id}")

    audit = AuditLog(
        actor_id=user.id,
        action="break_end",
        entity_type="break_session",
        entity_id=session.id,
    )
    db.add(audit)
    await db.flush()
    return session


async def check_overdue_breaks(db: AsyncSession) -> int:
    """Mark active breaks that passed planned_end as OVERDUE."""
    now = utc_now()
    result = await db.execute(
        select(BreakSession).where(
            and_(
                BreakSession.status == BreakStatus.ACTIVE,
                BreakSession.planned_end_at < now,
            )
        )
    )
    sessions = result.scalars().all()
    for s in sessions:
        s.status = BreakStatus.OVERDUE
        s.overdue_notified = True
    return len(sessions)
