from datetime import datetime, timedelta
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.notification import NotificationQueue, NotificationStatus, NotificationType
from app.services.whatsapp import whatsapp_service
from app.utils.time_utils import utc_now
from app.config import get_settings

settings = get_settings()


async def enqueue_notification(
    db: AsyncSession,
    phone: str,
    notification_type: NotificationType,
    message_body: str,
    user_id: int | None = None,
    scheduled_at: datetime | None = None,
    unique_key: str | None = None,
    template_name: str | None = None,
) -> NotificationQueue | None:
    """Add a notification to the queue. Returns None if unique_key already exists."""
    if unique_key:
        existing = await db.execute(
            select(NotificationQueue).where(NotificationQueue.unique_key == unique_key)
        )
        if existing.scalar_one_or_none():
            return None

    item = NotificationQueue(
        user_id=user_id,
        phone=phone,
        notification_type=notification_type,
        message_body=message_body,
        template_name=template_name,
        status=NotificationStatus.PENDING,
        scheduled_at=scheduled_at or utc_now(),
        unique_key=unique_key,
    )
    db.add(item)
    await db.flush()
    return item


async def process_pending_notifications(db: AsyncSession) -> int:
    """Process due notifications. Called by background worker every 30s."""
    now = utc_now()
    result = await db.execute(
        select(NotificationQueue)
        .where(
            and_(
                NotificationQueue.status == NotificationStatus.PENDING,
                NotificationQueue.scheduled_at <= now,
            )
        )
        .limit(50)
    )
    items = result.scalars().all()
    sent_count = 0

    for item in items:
        try:
            if item.template_name:
                await whatsapp_service.send_template(item.phone, item.template_name)
            else:
                await whatsapp_service.send_text(item.phone, item.message_body)
            item.status = NotificationStatus.SENT
            item.sent_at = utc_now()
            sent_count += 1
        except Exception as e:
            item.status = NotificationStatus.FAILED
            item.error_message = str(e)[:500]
        await db.flush()

    return sent_count


async def cancel_notifications_by_key_prefix(db: AsyncSession, prefix: str) -> int:
    """Cancel pending notifications whose unique_key starts with prefix."""
    result = await db.execute(
        select(NotificationQueue).where(
            and_(
                NotificationQueue.status == NotificationStatus.PENDING,
                NotificationQueue.unique_key.startswith(prefix),
            )
        )
    )
    items = result.scalars().all()
    for item in items:
        item.status = NotificationStatus.CANCELLED
    return len(items)
