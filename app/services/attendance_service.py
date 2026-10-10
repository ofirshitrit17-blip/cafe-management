from datetime import datetime
from sqlalchemy import select, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.attendance import AttendanceEvent, AttendanceEventType
from app.models.user import User
from app.models.audit import AuditLog
from app.utils.time_utils import utc_now, now_israel
from app.utils.ip_check import is_from_cafe_network


async def clock_in(
    db: AsyncSession,
    user: User,
    client_ip: str,
    source: str = "mobile",
) -> AttendanceEvent:
    if not is_from_cafe_network(client_ip) and source == "mobile":
        raise ValueError("החתמת כניסה מותרת רק מרשת בית הקפה או באמצעות קוד מהטאבלט")

    # Prevent double clock-in within 60 seconds
    recent = await db.execute(
        select(AttendanceEvent)
        .where(
            and_(
                AttendanceEvent.user_id == user.id,
                AttendanceEvent.event_type == AttendanceEventType.CLOCK_IN,
            )
        )
        .order_by(desc(AttendanceEvent.event_time))
        .limit(1)
    )
    last = recent.scalar_one_or_none()
    if last and (utc_now() - last.event_time).total_seconds() < 60:
        raise ValueError("כבר בוצעה החתמת כניסה לאחרונה")

    event = AttendanceEvent(
        user_id=user.id,
        event_type=AttendanceEventType.CLOCK_IN,
        event_time=utc_now(),
        source=source,
        ip_address=client_ip,
        is_late=False,  # can be calculated vs shift start later
    )
    db.add(event)

    audit = AuditLog(
        actor_id=user.id,
        action="clock_in",
        entity_type="attendance_event",
        details=f"source={source}, ip={client_ip}",
        ip_address=client_ip,
    )
    db.add(audit)
    await db.flush()
    return event


async def clock_out(
    db: AsyncSession,
    user: User,
    client_ip: str,
    source: str = "mobile",
) -> AttendanceEvent:
    event = AttendanceEvent(
        user_id=user.id,
        event_type=AttendanceEventType.CLOCK_OUT,
        event_time=utc_now(),
        source=source,
        ip_address=client_ip,
    )
    db.add(event)

    audit = AuditLog(
        actor_id=user.id,
        action="clock_out",
        entity_type="attendance_event",
        details=f"source={source}, ip={client_ip}",
        ip_address=client_ip,
    )
    db.add(audit)
    await db.flush()
    return event


async def get_today_status(db: AsyncSession, user_id: int) -> dict:
    today_start = now_israel().replace(hour=0, minute=0, second=0, microsecond=0)
    result = await db.execute(
        select(AttendanceEvent)
        .where(
            and_(
                AttendanceEvent.user_id == user_id,
                AttendanceEvent.event_time >= today_start.astimezone(utc_now().tzinfo) if False else AttendanceEvent.event_time >= today_start,
            )
        )
        .order_by(AttendanceEvent.event_time)
    )
    events = result.scalars().all()
    clocked_in = False
    last_in = None
    last_out = None
    for e in events:
        if e.event_type == AttendanceEventType.CLOCK_IN:
            clocked_in = True
            last_in = e.event_time
        elif e.event_type == AttendanceEventType.CLOCK_OUT:
            clocked_in = False
            last_out = e.event_time
    return {
        "is_clocked_in": clocked_in,
        "last_clock_in": last_in,
        "last_clock_out": last_out,
        "events": events,
    }
