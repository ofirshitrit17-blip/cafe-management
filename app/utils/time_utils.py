from datetime import datetime, date, time, timedelta
import pytz
from app.config import get_settings

settings = get_settings()
TZ = pytz.timezone(settings.TIMEZONE)


def now_israel() -> datetime:
    return datetime.now(TZ)


def utc_now() -> datetime:
    return datetime.now(pytz.UTC)


def to_israel(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        dt = pytz.UTC.localize(dt)
    return dt.astimezone(TZ)


def start_of_week(d: date | None = None) -> date:
    """Return Monday of the week for given date (or today)."""
    if d is None:
        d = now_israel().date()
    return d - timedelta(days=d.weekday())


def is_constraints_deadline_passed(week_start: date | None = None) -> bool:
    """Check if Wednesday 13:00 deadline has passed for the given week."""
    if week_start is None:
        week_start = start_of_week()
    # Deadline is Wednesday of that week at 13:00
    deadline_date = week_start + timedelta(days=settings.CONSTRAINTS_DEADLINE_WEEKDAY)
    deadline = TZ.localize(datetime.combine(
        deadline_date,
        time(settings.CONSTRAINTS_DEADLINE_HOUR, settings.CONSTRAINTS_DEADLINE_MINUTE)
    ))
    return now_israel() > deadline


def format_israel(dt: datetime) -> str:
    return to_israel(dt).strftime("%d/%m/%Y %H:%M")
